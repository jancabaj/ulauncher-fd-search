import subprocess
import os
from pathlib import Path
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.OpenAction import OpenAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction


class FastFileSearchExtension(Extension):

    def __init__(self):
        super(FastFileSearchExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        query = event.get_argument() or ""

        if not query or len(query) < 2:
            return RenderResultListAction([
                ExtensionResultItem(
                    icon='system-search',
                    name='File Search',
                    description='Type at least 2 characters to search files and folders',
                    on_enter=HideWindowAction()
                )
            ])

        # Get preferences
        search_path = extension.preferences.get('search_path', '~')
        search_path = os.path.expanduser(search_path)
        max_results = int(extension.preferences.get('max_results', 10))

        # Search using fd
        results = self.search_with_fd(query, search_path, max_results)

        if not results:
            return RenderResultListAction([
                ExtensionResultItem(
                    icon='system-search',
                    name='No results found',
                    description=f'No files or folders matching "{query}"',
                    on_enter=HideWindowAction()
                )
            ])

        items = []
        for result_path in results:
            path_obj = Path(result_path)

            # Determine if it's a file or directory and set appropriate icon
            if path_obj.is_dir():
                icon = 'images/folder.svg'
                item_type = 'Folder'
            else:
                icon = 'images/file.svg'
                item_type = 'File'

            # Get parent directory for description
            parent = str(path_obj.parent)

            items.append(
                ExtensionResultItem(
                    icon=icon,
                    name=path_obj.name,
                    description=f'{item_type}: {parent}',
                    on_enter=OpenAction(result_path)
                )
            )

        return RenderResultListAction(items)

    def search_with_fd(self, query, search_path, max_results):
        """Search for files and folders using fd command"""
        try:
            # Use fdfind on Ubuntu/Debian (fd is renamed to avoid conflict)
            fd_cmd = 'fdfind' if os.path.exists('/usr/bin/fdfind') else 'fd'

            # Run fd command
            # -H: include hidden files
            # -I: don't respect .gitignore
            # -t f: files, -t d: directories (we want both, so no -t flag)
            # --max-results: limit results
            cmd = [
                fd_cmd,
                '--max-results', str(max_results),
                '--color', 'never',
                '--full-path',
                query,
                search_path
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0:
                paths = [p.strip() for p in result.stdout.split('\n') if p.strip()]
                return paths
            else:
                return []

        except subprocess.TimeoutExpired:
            return []
        except Exception as e:
            print(f"Error running fd: {e}")
            return []


if __name__ == '__main__':
    FastFileSearchExtension().run()
