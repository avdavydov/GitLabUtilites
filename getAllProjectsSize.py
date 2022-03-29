import datetime
import config
import logging
import warnings
import gitlab
import pandas as pd

def loggingConfig(level):
    file_log = logging.FileHandler('SM-28427.log')
    console_out = logging.StreamHandler()
    logging.basicConfig(handlers=(file_log, console_out),
                        format='[%(asctime)s] [%(levelname)s] %(message)s',
                        datefmt='%d-%m-%Y %H:%M:%S',
                        level=level)


def fetchProjectsSize(gl, page, per_page) -> list:
    result = []
    for project in gl.projects.list(page=page, per_page=per_page, statistics=True):
        attributes = project.attributes
        id = attributes.get('id')
        web_url = attributes.get('web_url')
        statistics = project.statistics
        repository_size = statistics.get('repository_size')
        result.append([id, repository_size, web_url])
    return result


def getAllRepoSize(gl) -> pd.DataFrame:
    loggingConfig(logging.INFO)
    result = []
    per_page = 100
    page = 1
    while True:
        logging.info(f'Запрос данных. Страница {page}')
        projects_info = fetchProjectsSize(gl=gl, page=page, per_page=per_page)
        logging.info(f'Для страницы {page} получено записей: {len(projects_info)}')

        if len(projects_info) == 0:
            break
        else:
            result = [res for res in result + projects_info]
            page += 1

    result = sorted(result, key=lambda x: x[1], reverse=True)
    result_df = pd.DataFrame(result, columns=['id', 'repository_size', 'web_url'])
    return result_df


def saveToExcel(df, file_name, add_date=None) -> None:
    if add_date:
        file_name = file_name.replace('.xlsx', ' ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '.xlsx')
    loggingConfig(logging.INFO)
    logging.info('Выгрузка отчёта')
    writer = pd.ExcelWriter(file_name, engine='xlsxwriter', options={'strings_to_urls': False})
    df.to_excel(writer, index=False)
    writer.save()
    logging.info(f'Отчёт сформирован. Размер отчёта: {df.shape}')
    logging.info(f'Результат выгружен в файл: {file_name}')


def main():
    warnings.filterwarnings("ignore")
    url = config.git_lab_url
    token = config.git_lab_token
    gl = gitlab.Gitlab(url, token)
    pd_df = getAllRepoSize(gl=gl)
    file_name = '~/Downloads/Result.xlsx'
    saveToExcel(df=pd_df, file_name=file_name)


if __name__ == '__main__':
    main()
