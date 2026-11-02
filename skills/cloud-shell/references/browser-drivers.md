# Firefox·Chromium과 WebDriver 설치 및 검증

## 원칙

- 브라우저, WebDriver, 화면 표시 서버(noVNC/디스플레이), CDP는 별개다. Firefox 컨테이너의 브라우저는 별도 컨테이너 안에 있으므로 Cloud Shell 호스트에 geckodriver가 설치된 것이 아니다.
- 기존 환경을 먼저 확인해 사용자의 프로필, 가상환경과 실행 중 브라우저를 보존한다. 버전과 경로를 보고 실패 지점을 분리한다. 기존 브라우저에 붙거나 사이트에 로그인하지 않는다.
- Selenium Manager는 드라이버가 없을 때 브라우저와 호환되는 드라이버를 찾고 필요하면 다운로드해 사용자 캐시에 저장한다. 자동 다운로드에는 지원되는 아키텍처와 인터넷 연결이 필요하며 실패할 수 있다. [공식 Selenium Manager 안내](https://www.selenium.dev/documentation/selenium_manager/).
- Chromium을 명시적으로 요청하면 Chrome for Testing을 Chromium이라고 부르지 않는다. 기존 Chromium의 실제 실행 파일을 `--chromium`으로 지정한다. Selenium Manager가 제공하는 Chrome은 다른 브라우저다.

## 설치와 실행

1. `command -v chromium chromium-browser google-chrome firefox`와 각 실행 파일의 `--version`으로 사용 가능한 브라우저를 확인한다. 배포판과 아키텍처도 확인한다. 없는 Firefox는 [Mozilla 공식 Linux 설치 안내](https://support.mozilla.org/en-US/kb/install-firefox-linux)를 따른다. 기존 snap을 삭제하거나 시스템 저장소 우선순위를 변경하기 전에 사용자의 설치 의도와 환경을 확인한다. Ubuntu 24.04의 `chromium-browser`는 snap 전환 패키지이므로 컨테이너 환경에서 작동한다고 가정하지 않는다. Cloud Shell의 일시적 시스템 패키지, Selenium Manager의 Linux 아키텍처·네트워크 제약을 점검한다.
2. 별도의 사용자 가상환경을 만든다. `python3 -m venv "$HOME/.venvs/cloud-shell-browser"` 후 `"$HOME/.venvs/cloud-shell-browser/bin/python" -m pip install -U selenium`을 실행한다. 홈 디렉터리에 설치해 기본 Cloud Shell 모드에서 유지한다.

Chromium이 없다면 별도 시스템 저장소를 추가하지 않는 대안으로 이 가상환경에서 `python -m pip install playwright`, `python -m playwright install chromium`을 실행해 Playwright의 Chromium 빌드를 사용자 캐시에 내려받을 수 있다. 위 명령들의 `python`은 가상환경의 전체 Python 경로로 대체한다. 실행 파일은 다음으로 확인한다.

```bash
"$HOME/.venvs/cloud-shell-browser/bin/python" -c 'from playwright.sync_api import sync_playwright; p=sync_playwright().start(); print(p.chromium.executable_path); p.stop()'
```

이는 Playwright용 Chromium이며 WebDriver가 아니다. Selenium Manager가 이에 호환되는 chromedriver를 구하지 못할 수도 있으므로 다음 단계의 실제 WebDriver 테스트로 검증하고, 실패하면 정확한 버전·오류를 보고한다. [Playwright 브라우저 설치](https://playwright.dev/python/docs/browsers).
3. 스킬 폴더의 `scripts/verify_webdrivers.py`를 가상환경 Python으로 실행한다. `--chromium`에는 발견한 Chromium의 실제 경로를 전달한다. Firefox 경로가 PATH에 없으면 `--firefox`도 지정한다.

```bash
"$HOME/.venvs/cloud-shell-browser/bin/python" \
  /path/to/cloud-shell/scripts/verify_webdrivers.py \
  --chromium /path/to/chromium --firefox /path/to/firefox
```

실제 설치 위치로 `/path/to`를 교체한다. 검증 스크립트는 독립적 headless 프로필에서 Firefox와 Chromium을 각각 실행하고 `data:` 테스트 페이지 제목을 검사한 뒤 브라우저와 드라이버 버전을 출력하고 종료한다. 드라이버가 없다면 Selenium Manager가 설치를 시도한다. 둘 중 하나라도 실패하면 0이 아닌 종료 코드를 돌려준다. 드라이버가 PATH가 아니라 `~/.cache/selenium`에 있을 수 있다.

4. 두 브라우저 모두 성공한 경우에만 드라이버 검증이 완료됐다고 말한다. 오류가 나면 어느 브라우저의 설치·드라이버 다운로드·시작·페이지 확인 단계에서 실패했는지 기록하고, 실제 오류에 맞춰 의존성·버전 호환성·네트워크를 해결한다. `--no-sandbox` 같은 보안 완화는 자동 적용하지 않는다.
5. 화면 표시도 요청되었다면 별도로 디스플레이와 인증된 원격 보기 연결을 마련하고 실제 화면을 확인한다. Headless 검증 성공만으로 GUI가 동작한다고 말하지 않는다. Cloud Shell 재시작 시 프로세스는 사라진다.
