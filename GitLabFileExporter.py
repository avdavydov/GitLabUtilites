import os
import time
from pathlib import Path
import gitlab

import config

URL = config.git_lab_url
TOKEN = config.git_lab_token
BRANCH_NAME = config.branch_name
GROUP_ID = config.group_id
MAIN_DIR = config.main_dir


def main():
    gl = gitlab.Gitlab(URL, TOKEN)
    start = time.time()
    home_dir = Path.home()
    group = gl.groups.get(GROUP_ID, lazy=True)
    projects = group.projects.list(include_subgroups=True, all=True)

    for project in projects:
        project_id = project.id
        prj = gl.projects.get(project_id)
        try:
            items = prj.repository_tree(path='src', ref=BRANCH_NAME, all=True, recursive=True)
        except (gitlab.exceptions.GitlabGetError, gitlab.exceptions.GitlabHttpError):
            print(f'Tree for project with ID={project_id} not found')
            items = None

        if items is not None:
            for item in items:
                if item.get('type') != 'tree':
                    file_name_with_path = Path(home_dir, MAIN_DIR, project.path_with_namespace, item.get('path'))
                    full_file_path = file_name_with_path.parent
                    print(file_name_with_path, end=' ')

                    try:
                        os.makedirs(full_file_path, exist_ok=True)
                    except OSError:
                        os.remove(full_file_path)
                        os.makedirs(full_file_path, exist_ok=True)

                    try:
                        with open(file_name_with_path, 'wb') as file:
                            prj.files.raw(file_path=item.get('path'), ref=BRANCH_NAME, streamed=True, action=file.write)
                    except (gitlab.exceptions.GitlabGetError, gitlab.exceptions.GitlabHttpError):
                        print(' - Error')
                    print(' - Done')

    print('========================', 'Done', sep='\n')
    print(f'Общая длительность выполнения скрипта {int(time.time() - start)} секунд')


if __name__ == '__main__':
    main()
