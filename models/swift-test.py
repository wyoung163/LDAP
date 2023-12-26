import logging
import pprint
from os import walk
from os.path import join
from swiftclient.multithreading import OutputManager
from swiftclient.service import SwiftService, SwiftError, SwiftUploadObject
from sys import argv

logging.basicConfig(level=logging.ERROR)
logging.getLogger("requests").setLevel(logging.CRITICAL)
logging.getLogger("swiftclient").setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)

container = argv[1]
objects = argv[2:]

# the use of stat to retrieve the headers for a given list of objects in a container using 20 threads
_opts = {'object_dd_threads': 20}
with SwiftService(options=_opts) as swift:
    header_data = {}
    stats_it = swift.stat(container=container, objects=objects)
    for stat_res in stats_it:
        if stat_res['success']:
            header_data[stat_res['object']] = stat_res['headers']
        else:
            logger.error(
                'Failed to retrieve stats for %s' % stat_res['object']
            )
    pprint.pprint(header_data)

#  list to list all items in a container that are over 10MiB in size
minimum_size = 10*1024**2
with SwiftService() as swift:
    try:
        list_parts_gen = swift.list(container=container)
        for page in list_parts_gen:
            if page["success"]:
                for item in page["listing"]:

                    i_size = int(item["bytes"])
                    if i_size > minimum_size:
                        i_name = item["name"]
                        i_etag = item["hash"]
                        print(
                            "%s [size: %s] [etag: %s]" %
                            (i_name, i_size, i_etag)
                        )
            else:
                raise page["error"]

    except SwiftError as e:
        logger.error(e.value)

## post
with SwiftService() as swift:
    try:
        list_options = {"prefix": "archive_2016-01-01/"}
        list_parts_gen = swift.list(container=container)
        for page in list_parts_gen:
            if page["success"]:
                objects = [obj["name"] for obj in page["listing"]]
                post_options = {"header": "X-Delete-After:86400"}
                for post_res in swift.post(
                        container=container,
                        objects=objects,
                        options=post_options):
                    if post_res['success']:
                        print("Object '%s' POST success" % post_res['object'])
                    else:
                        print("Object '%s' POST failed" % post_res['object'])
            else:
                raise page["error"]
    except SwiftError as e:
        logger.error(e.value)

## download
def is_png(obj):
    return (
        obj["name"].lower().endswith('.png') or
        obj["content_type"] == 'image/png'
    )
with SwiftService() as swift:
    try:
        list_options = {"prefix": "archive_2016-01-01/"}
        list_parts_gen = swift.list(container=container)
        for page in list_parts_gen:
            if page["success"]:
                objects = [
                    obj["name"] for obj in page["listing"] if is_png(obj)
                ]
                for down_res in swift.download(
                        container=container,
                        objects=objects):
                    if down_res['success']:
                        print("'%s' downloaded" % down_res['object'])
                    else:
                        print("'%s' download failed" % down_res['object'])
            else:
                raise page["error"]
    except SwiftError as e:
        logger.error(e.value)

## upload
dir = argv[1]
_opts = {'object_uu_threads': 20}
with SwiftService(options=_opts) as swift, OutputManager() as out_manager:
    try:
        # Collect all the files and folders in the given directory
        objs = []
        dir_markers = []
        for (_dir, _ds, _fs) in walk(dir):
            if not (_ds + _fs):
                dir_markers.append(_dir)
            else:
                objs.extend([join(_dir, _f) for _f in _fs])

        # Now that we've collected all the required files and dir markers
        # build the ``SwiftUploadObject``s for the call to upload
        objs = [
            SwiftUploadObject(
                o, object_name=o.replace(
                    dir, 'my-%s-objects' % dir, 1
                )
            ) for o in objs
        ]
        dir_markers = [
            SwiftUploadObject(
                None, object_name=d.replace(
                    dir, 'my-%s-objects' % dir, 1
                ), options={'dir_marker': True}
            ) for d in dir_markers
        ]

        # Schedule uploads on the SwiftService thread pool and iterate
        # over the results
        for r in swift.upload(container, objs + dir_markers):
            if r['success']:
                if 'object' in r:
                    print(r['object'])
                elif 'for_object' in r:
                    print(
                        '%s segment %s' % (r['for_object'],
                                           r['segment_index'])
                        )
            else:
                error = r['error']
                if r['action'] == "create_container":
                    logger.warning(
                        'Warning: failed to create container '
                        "'%s'%s", container, error
                    )
                elif r['action'] == "upload_object":
                    logger.error(
                        "Failed to upload object %s to container %s: %s" %
                        (container, r['object'], error)
                    )
                else:
                    logger.error("%s" % error)

    except SwiftError as e:
        logger.error(e.value)


## delete
_opts = {'object_dd_threads': 20}
with SwiftService(options=_opts) as swift:
    del_iter = swift.delete(container=container, objects=objects)
    for del_res in del_iter:
        c = del_res.get('container', '')
        o = del_res.get('object', '')
        a = del_res.get('attempts')
        if del_res['success'] and not del_res['action'] == 'bulk_delete':
            rd = del_res.get('response_dict')
            if rd is not None:
                t = dict(rd.get('headers', {}))
                if t:
                    print(
                        'Successfully deleted {0}/{1} in {2} attempts '
                        '(transaction id: {3})'.format(c, o, a, t)
                    )
                else:
                    print(
                        'Successfully deleted {0}/{1} in {2} '
                        'attempts'.format(c, o, a)
                    )