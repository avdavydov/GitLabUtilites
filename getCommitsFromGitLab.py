import gitlab
from pathlib import Path

import config

URL = config.git_lab_url
TOKEN = config.git_lab_token
GROUP_ID = config.group_id
BRANCH_NAME = config.branch_name
MAIN_DIR = config.main_dir
OUTPUT_FILE_NAME = config.output_file_name

gl = gitlab.Gitlab(URL, TOKEN)


def getCommiters(project_id, gl, branch_name):
    committers = set()
    prj = gl.projects.get(project_id)
    commits = prj.commits.list(ref_name=branch_name)
    for commit in commits:
        if commit.committer_name.lower() != 'administrator':
            committers.add(commit.committer_name)
    return committers

def main():
    group = gl.groups.get(GROUP_ID, lazy=True)
    projects = group.projects.list(include_subgroups=True, all=True)

    with open(Path(Path.home(), MAIN_DIR, OUTPUT_FILE_NAME), 'w+') as file:
        for project in projects:
            print(project.path_with_namespace, project.id, ', '.join(sorted(getCommiters(project.id, gl, BRANCH_NAME))), file=file,
                  sep=';')
    print('Done.')

if __name__ == '__main__':
    main()