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
            try:
                path_obj = Path(result_path)

                # Skip if path no longer exists
                if not path_obj.exists():
                    continue

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
            except Exception as e:
                # Skip items that cause errors
                print(f"Error processing {result_path}: {e}")
                continue

        return RenderResultListAction(items)

    def search_with_fd(self, query, search_path, max_results):
        """Search for files and folders using fd command"""
        try:
            # Use fdfind on Ubuntu/Debian (fd is renamed to avoid conflict)
            fd_cmd = 'fdfind' if os.path.exists('/usr/bin/fdfind') else 'fd'

            # Validate search path exists
            if not os.path.exists(search_path):
                return []

            # Run fd command
            # --max-results: limit results
            # --color: disable color output
            # --full-path: search in full path
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
                timeout=1,  # Reduced timeout to 1 second
                check=False
            )

            if result.returncode == 0 and result.stdout:
                paths = [p.strip() for p in result.stdout.split('\n') if p.strip()]
                return paths[:max_results]  # Ensure we don't exceed max_results
            else:
                return []

        except subprocess.TimeoutExpired:
            print(f"fd search timed out for query: {query}")
            return []
        except FileNotFoundError:
            print(f"fd command not found")
            return []
        except Exception as e:
            print(f"Error running fd: {e}")
            return []


if __name__ == '__main__':
    FastFileSearchExtension().run()
