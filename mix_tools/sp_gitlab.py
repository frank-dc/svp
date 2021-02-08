import gitlab
import json
import os
from container.configs import gitlab_url, gitlab_token


def init_gitlab(git_url=f'http://{gitlab_url}', git_token=gitlab_token):
    gl = gitlab.Gitlab(git_url, private_token=git_token)
    assert gl.version()[0] != 'unknown', 'gitlab connection failure'
    return gl


def retrieve_commits(pid=None, branch=None, expect_ret=['id', 'message']):
    """
    根据项目ID获取指定返回
    :param pid: gitlab project id
    :param branch: 分支名称
    :param expect_ret: 获取commit.attributes中指定的key
    :return:
    """
    results = []
    gl = init_gitlab()
    try:
        p = gl.projects.get(id=pid)
        commits = p.commits.list(page=1, per_page=10, query_parameters={'ref_name': branch})
        for commit in commits:
            ca = {}
            for key, value in commit.attributes.items():
                if key in expect_ret:
                    ca.update({key: value})
            results.append(ca)
        return {
            'code': 0,
            'msg': '请求成功',
            'results': results
        }
    except Exception as e:
        return {
            'code': 1,
            'msg': '请求失败',
            'results': str(e)
        }

def get_branches(pid):
    try:
        gl = init_gitlab()
        ins = gl.projects.get(id=pid)
        branches = [item.name for item in ins.branches.list(all=True)]
    except Exception as e:
        branches = []
    return branches

def get_tags(pid):
    try:
        gl = init_gitlab()
        ins = gl.projects.get(id=pid)
        tags = [item.name for item in ins.tags.list(all=True)]
    except Exception as e:
        tags = []
    return tags


def get_project_id(name):
    """
    根据项目名称获取id
    先从缓存取，有通过接口认证，没有通过接口获取
    :param name: 项目名称
    :return:
    """
    gitlab_projects_cache = '/data/.cache/gitlab_projects.json'

    def get_id_by_name(name):
        gl = init_gitlab()
        projects = gl.projects.list(all=True)
        for item in projects:
            if item.name == name:
                id = item.id
                return id
        raise Exception("id of <%s> dosen't exist!" % name)

    def get_name_by_id(id):
        gl = init_gitlab()
        ins = gl.projects.get(id=id)
        return ins.name

    def dump_cache(content):
        with open(gitlab_projects_cache, 'w+') as f:
            json.dump(content, f)

    def load_cache():
        with open(gitlab_projects_cache, 'r') as f:
            content = json.load(f)
        return content


    if os.path.isfile(gitlab_projects_cache):
        # 缓存取
        content = load_cache()
        if content.get(name, None):
            id = content[name]
            new_name = get_name_by_id(id)
            if name == new_name:
                return id
            else:
                new_id = get_id_by_name(name)
                content.update({name: new_id})
                dump_cache(content)
                return new_id
        else:
            new_id = get_id_by_name(name)
            content.update({name: new_id})
            dump_cache(content)
            return new_id

    else:
        # 接口取
        gl = init_gitlab()
        content = {}
        projects = gl.projects.list(all=True)
        for item in projects:
            content.update({item.name: item.id})
        dump_cache(content)
        return get_id_by_name(name)


def cat_repository_file(pid, fp, branch='master'):
    gl = init_gitlab()
    ins = gl.projects.get(id=pid)
    content = ins.files.get(fp, ref=branch).decode()
    if isinstance(content, bytes):
        return content.decode()
    else:
        return content


if __name__ == '__main__':
    # content = cat_repository_file('3rd_login', 'Jenkinsfile')
    # print(content)
    id = get_project_id('DBA')
    print(id)