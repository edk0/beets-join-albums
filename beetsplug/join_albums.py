from collections import defaultdict

from beets.plugins import BeetsPlugin
from beets.ui import Subcommand
from beets import ui


class JoinPlugin(BeetsPlugin):
    def commands(self):
        join_command = Subcommand('join', help='merge albums')
        join_command.parser.add_option(
            '-n', '--dry-run',
            dest='dry_run',
            action='store_true',
            help="don't do anything"
        )
        join_command.parser.add_option(
            '-j', '--join',
            dest='join_fields',
            action='append',
            help="merge albums if they share a value for all fields named with -j"
        )
        join_command.func = self._join_command
        return [join_command]

    def _join_command(self, lib, opts, args):
        selection = lib.albums(ui.decargs(args))
        if opts.join_fields:
            groups = self._groupby(selection, opts.join_fields)
        else:
            groups = [selection]
        for group in groups:
            if len(group) < 2:
                continue
            self._do_merge(lib, group, opts.dry_run)

    def _groupby(self, items, fields):
        def key(x):
            return tuple(x[f] for f in fields)
        d = defaultdict(list)
        for item in items:
            d[key(item)].append(item)
        for key in list(d.keys()):
            if '' in key:
                del d[key]
        return list(d.values())

    def _do_merge(self, lib, albums, dry_run):
        sort = lib.get_default_album_sort()
        if not albums:
            raise ValueError
        print(f"Merge {len(albums)} albums:")
        for album in albums:
            print(f"  {album.albumartist} - {album.album}:")
            for item in sort.sort(album.items()):
                print(f"    {item.track:3d}: {item.title}")
        if dry_run:
            print("(dry run, breaking early)")
            return
        all_items = [item for album in albums for item in album.items()]
        lib.add_album(all_items)
        for album in albums:
            album.remove(delete=False, with_items=False)

