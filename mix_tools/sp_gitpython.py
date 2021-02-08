from git import Repo
from urllib import parse
import os

from small_platform.settings import BASE_DIR
from mix_tools.sp_subprocess import popen

web_dir = os.path.join(os.path.dirname(BASE_DIR), 'WebDir')
user = 'ptweb'
group = 'ptweb'

def git_update(project, git_url, version, branch='master'):
    """
    git python api
    :return:
    """
    git_log = ''    # 操作日志
    projects_list = os.listdir(web_dir)
    project_dir = os.path.join(web_dir, project)
    if project not in projects_list:
        try:
            repo = Repo.clone_from(git_url, project_dir, branch=branch)
            if isinstance(repo, Repo):
                git_log += '# 执行git clone\n%s\n' % repo
                try:
                    reset_ret = repo.git.reset('--hard', version)
                    git_log += '# 执行git reset\n%s\n' % reset_ret
                except Exception as e:
                    git_log += '# 执行git reset异常：\n%s\n' % str(e)
                    return {
                        'code': 1,
                        'msg': '执行git reset异常！',
                        'results': str(e)
                    }
            else:
                return {
                    'code': 1,
                    'msg': 'Repo.clone_from返回错误！',
                    'results': type(repo)
                }

        except Exception as e:
            git_log += '# 执行git clone异常：\n%s\n' % str(e)
            return {
                'code': 1,
                'msg': '执行git clone异常！',
                'results': str(e)
            }
    else:
        repo = Repo(project_dir)
        if repo.is_dirty():
            reset_ret = repo.git.reset('--hard')
            git_log += '# 工作区有更改，执行git reset\n%s\n' % reset_ret
        else:
            try:
                branches_existed = repo.git.branch()
                if branch in branches_existed:
                    repo.git.checkout(branch)
                    git_log += f"# 分支{branch}已存在，执行切换\n"
                else:
                    repo.git.pull()     # 新增分支，先pull，否则追踪会报错
                    repo.git.checkout('-t', 'origin/%s' % branch)   # 追踪一个远端分支
                    git_log += f"# 新建分支{branch}并追踪分支origin/{branch}，执行切换\n"
                branches_existed = repo.git.branch()
                if '* %s' % branch in branches_existed:
                    git_log += "# 切换到分支'%s'\n" % branch
                else:
                    return {
                        'code': 1,
                        'msg': "切换到分支'%s'异常！" % branch,
                        'results': branches_existed
                    }

                # repo.remote().pull()
                pull_ret = repo.git.pull()
                git_log += '# 执行git pull\n%s\n' % pull_ret
                try:
                    reset_ret = repo.git.reset('--hard', version)
                    git_log += '# 执行git reset\n%s\n' % reset_ret
                except Exception as e:
                    git_log += '# 执行git reset异常：\n%s\n' % str(e)
                    return {
                        'code': 1,
                        'msg': '执行git reset异常！',
                        'results': str(e)
                    }
            except Exception as e:
                git_log += '# 执行git pull异常：\n%s\n' % str(e)
                return {
                    'code': 1,
                    'msg': '执行git pull异常！',
                    'results': str(e)
                }
    # 记录版本号
    try:
        version_path = os.path.join(project_dir, 'Gversion.txt')
        with open(version_path, 'w') as f:
            f.write(version)
            f.write('\n')
        git_log += "# 记录版本号：%s\n" % version
    except Exception as e:
        git_log += "# 记录版本号失败：%s\n" % str(e)
    # 代码属主修改
    chown_ret = popen('chown -R %s:%s %s' % (user, group, project_dir))
    if chown_ret['code'] == 1:
        return chown_ret
    else:
        git_log += chown_ret['msg']
        return {
            'code': 0,
            'msg': '代码更新完成',
            'results': git_log
        }

if __name__ == '__main__':
    pass
