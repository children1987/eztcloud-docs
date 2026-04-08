#!/usr/bin/env bash

# 若不是在 bash 中运行，自动切换到 bash 重启脚本
if [ -z "${BASH_VERSION:-}" ]; then
  exec bash "$0" "$@"
fi

set -eu

# 兼容不支持 pipefail 的 shell
if (set -o pipefail) 2>/dev/null; then
  set -o pipefail
fi

if [ "${EUID:-$(id -u)}" -ne 0 ]; then
  echo "请使用 root 用户或 sudo 运行 setup.sh"
  exit 1
fi

if [ -f /etc/os-release ]; then
  # shellcheck disable=SC1091
  . /etc/os-release
else
  echo "无法识别系统：缺少 /etc/os-release"
  exit 1
fi

PKG_MGR=""
UPDATE_CMD=""
INSTALL_GIT_CMD=""

case "${ID:-}" in
  ubuntu|debian)
    PKG_MGR="apt"
    UPDATE_CMD="apt update"
    INSTALL_GIT_CMD="apt install -y git"
    ;;
  centos|rhel|rocky|almalinux|ol)
    PKG_MGR="yum"
    UPDATE_CMD="yum check-update || true"
    INSTALL_GIT_CMD="yum install -y git"
    ;;
  *)
    case " ${ID_LIKE:-} " in
      *" debian "*)
        PKG_MGR="apt"
        UPDATE_CMD="apt update"
        INSTALL_GIT_CMD="apt install -y git"
        ;;
      *" rhel "*|*" fedora "*)
        PKG_MGR="yum"
        UPDATE_CMD="yum check-update || true"
        INSTALL_GIT_CMD="yum install -y git"
        ;;
      *)
        echo "暂不支持该系统：ID=${ID:-unknown}, ID_LIKE=${ID_LIKE:-unknown}"
        exit 1
        ;;
    esac
    ;;
esac

echo "检测到系统：${PRETTY_NAME:-unknown}，将使用 ${PKG_MGR}"

eval "${UPDATE_CMD}"
eval "${INSTALL_GIT_CMD}"

mkdir -p /workspace
cd /workspace
rm -rf isw-helper
git clone https://hongtanzhineng:cad321168656fdf0fd24490c7378de05@gitee.com/hotanzn/isw-helper.git isw-helper
cd isw-helper

exec bash quick_start.sh "$@"
