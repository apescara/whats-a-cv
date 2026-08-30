import os
import pwd
import sys


user = pwd.getpwnam("app")
os.environ["HOME"] = user.pw_dir
os.environ["UV_CACHE_DIR"] = "/tmp/uv-cache"
state = "/workspace/.whats-a-cv"
os.makedirs(state, exist_ok=True)
os.chown(state, user.pw_uid, user.pw_gid)
for root, directories, files in os.walk(state):
    for name in directories + files:
        os.chown(os.path.join(root, name), user.pw_uid, user.pw_gid, follow_symlinks=False)
os.setgid(user.pw_gid)
os.setuid(user.pw_uid)
os.execvp(sys.argv[1], sys.argv[1:])
