# setup_windows_links.py

import os
from pathlib import Path
from typing import Optional


class WindowsFolderLinker:
    def __init__(self, wsl_base_path: Path, windows_user: str):
        self.wsl_base_path = Path(wsl_base_path)
        self.windows_user = windows_user
        self.windows_drive_prefix = "/mnt/c/Users/"

    def _get_windows_path(self, folder_name: str) -> Path:
        """주어진 폴더 이름으로 Windows 절대 경로를 반환합니다."""
        return Path(f"{self.windows_drive_prefix}{self.windows_user}/{folder_name}")

    def create_link(self, target_folder_name: str, link_name: Optional[str] = None) -> bool:
        """
        Windows 폴더에 대한 심볼릭 링크를 WSL Git 저장소에 생성합니다.
        target_folder_name: Windows 사용자 폴더 하위의 폴더 이름 (예: Downloads, Pictures)
        link_name: WSL Git 저장소 내에서 생성될 링크 이름 (기본값은 target_folder_name)
        """
        if link_name is None:
            link_name = target_folder_name

        windows_path = self._get_windows_path(target_folder_name)
        wsl_link_path = self.wsl_base_path / link_name

        # 심볼릭 링크의 대상이 되는 Windows 폴더가 존재하는지 확인
        if not windows_path.is_dir():  # is_dir()로 디렉토리인지 정확히 확인
            print(f"경고: Windows 디렉토리 '{windows_path}'를 찾을 수 없거나 디렉토리가 아닙니다. 스킵합니다.")
            return False

        # WSL Git 저장소 내에 이미 링크가 존재하는지 확인
        if wsl_link_path.exists():
            if wsl_link_path.is_symlink():
                # 이미 존재하는 심볼릭 링크이고, 대상이 같다면 스킵
                if os.readlink(wsl_link_path) == str(windows_path):
                    print(f"정보: WSL 링크 '{wsl_link_path}'가 이미 존재하며 대상이 동일합니다. 스킵합니다.")
                    return True
                else:
                    # 링크는 존재하지만 대상이 다르다면 경고 후 스킵 (또는 덮어쓰기 로직 추가 가능)
                    print(f"경고: WSL 링크 '{wsl_link_path}'가 다른 대상을 가리킵니다. 스킵합니다.")
                    return False
            else:
                # 같은 이름의 파일/폴더가 이미 존재하면 경고
                print(f"경고: WSL 경로 '{wsl_link_path}'에 이미 파일/폴더가 존재합니다. 스킵합니다.")
                return False

        try:
            os.symlink(windows_path, wsl_link_path)
            print(f"심볼릭 링크 생성 성공: '{windows_path}' -> '{wsl_link_path}'")
            return True
        except OSError as e:
            print(f"심볼릭 링크 생성 실패 ({windows_path} -> {wsl_link_path}): {e}")
            return False


# 사용 예시:
if __name__ == "__main__":
    windows_user_account = "deity"  # 확인된 사용자 계정명

    # wsl_dotfiles_dir = os.path.expanduser("~/windows_dotfiles")
    # 스크립트가 실행되는 현재 디렉토리를 wsl_dotfiles_dir로 설정
    # os.path.dirname(os.path.abspath(__file__))는 스크립트의 디렉토리 경로를 반환합니다.
    # 이 경우 'src' 디렉토리가 됩니다.
    # 만약 'src' 디렉토리 자체가 아닌 'window-dotfiles' 디렉토리 하위에 만들고 싶다면,
    # Path(__file__).parent.parent 와 같이 부모 디렉토리를 지정해야 합니다.
    # 개발자님의 'll' 출력을 보니 '/home/deity719/para/resource/window-dotfiles/src'에서 스크립트가 실행되고 있으므로,
    # './' (현재 디렉토리)를 기준으로 링크를 만들면 원하는 위치가 됩니다.
    wsl_dotfiles_dir = Path(os.getcwd())  # 현재 작업 디렉토리를 사용

    # Git 저장소 디렉토리 생성
    if not Path(wsl_dotfiles_dir).exists():
        os.makedirs(wsl_dotfiles_dir)
        print(f"Git 저장소 디렉토리 생성: {wsl_dotfiles_dir}")

    linker = WindowsFolderLinker(wsl_dotfiles_dir, windows_user_account)

    # 심볼릭 링크로 관리하고 싶은 모든 Windows 디렉토리 목록
    # 'll' 출력에서 'drwxrwxrwx'로 시작하는 디렉토리들을 주로 포함합니다.
    # 'Application Data', 'Cookies', 'Local Settings', 'My Documents', 'NetHood',
    # 'PrintHood', 'Recent', 'SendTo', 'Templates', '시작 메뉴' 등은 이미 심볼릭 링크이거나
    # AppData 내부에 있는 경우도 있으므로, 중복 관리나 불필요한 관리를 피하기 위해 직접 포함하지 않습니다.
    # 주로 사용자에게 직접 보이는 중요 폴더들을 대상으로 합니다.
    windows_folders_to_link = [
        "Contacts",
        "Desktop",
        "Documents",
        "Downloads",
        "Favorites",
        # "IntelGraphicsProfiles", # 특정 그래픽 프로파일은 관리할 필요가 있을 수 있음
        "Links",
        "Music",
        # "OneDrive", # OneDrive 동기화는 OneDrive 자체에서 관리되므로 Git으로 중복 관리가 필요 없을 수 있음.
        # 만약 OneDrive 내 특정 폴더만 관리한다면 그 폴더를 명시하는 것이 좋습니다.
        "Pictures",
        "Saved Games",
        "Searches",
        "Videos",
        # 필요하다면 다른 디렉토리도 추가
        ".vscode",  # VSCode 설정도 .dotfiles처럼 관리하면 유용할 수 있습니다.
        # "AppData", # AppData는 매우 크고 변경이 잦으며, Git으로 관리하기에 적합하지 않을 수 있습니다.
        # 특정 AppData 하위 폴더만 관리하는 것을 고려하세요.
    ]

    for folder in windows_folders_to_link:
        linker.create_link(folder)

    # 특별히 다른 이름을 사용하고 싶다면:
    # linker.create_link("Downloads", "My_Downloads_Link")
