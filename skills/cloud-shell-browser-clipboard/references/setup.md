# 설치와 테스트

이 절차는 별도의 X11 세션을 만들 때의 예시다. 기존 환경이 있다면 프로필과 프로세스를 먼저 확인해 재사용 여부를 결정한다. 임의로 기존 8080, 6080, 5900, 9222 또는 디스플레이 `:99`를 차지하거나 종료하지 않는다. 기본 Cloud Shell은 홈 이외의 설치 상태가 재설정될 수 있다.

## 1. 상태 확인과 준비

`docker ps`, `ps`, `ss -ltn` 등으로 기존 구성과 포트 충돌을 확인한다. `command -v x11vnc Xvfb xclip xdotool websockify`와 `x11vnc -help`로 도구 및 클립보드 옵션을 확인한다. 기존 프로필 경로와 로그인 데이터는 사용자에게 확인하고 변경하지 않는다.

Ubuntu Cloud Shell에서 필요한 시스템 도구가 없다면 사용자가 설치하도록 안내한다. 환경에 따라 패키지명이나 GUI 의존성은 다를 수 있다.

```bash
sudo apt update
sudo apt install -y xvfb x11vnc xclip xdotool openbox novnc websockify python3-venv fonts-noto-cjk
```

Chromium이 없다면 공식 설치 경로를 확인한다. Playwright Chromium은 기본적으로 `~/.cache/ms-playwright/`에 있을 수 있다. 실제 실행 파일을 확인하고 기존 브라우저를 함부로 교체하지 않는다.

스킬 디렉터리를 Cloud Shell 홈에 복사하거나 사용자가 신뢰하는 저장소에서 가져온다. 아래 예시의 `SKILL_DIR`을 그 실제 경로로 지정한다. 사용자 홈에 가상환경과 신규 전용 프로필을 마련한다. 기존 프로필이 있는 경우 삭제하거나 덮어쓰지 않는다.

```bash
SKILL_DIR="$HOME/.codex/skills/cloud-shell-browser-clipboard"
python3 -m venv "$HOME/.venvs/cloud-shell-clipboard"
"$HOME/.venvs/cloud-shell-clipboard/bin/python" -m pip install aiohttp
mkdir -p "$HOME/cloud-shell-browser/profile"
```

## 2. 공유 브라우저와 로컬 서비스

다음은 네 포트와 `:99`가 비어 있고 신규 전용 프로필을 사용하는 경우의 순서다. `CHROMIUM_BIN`은 확인한 실제 실행 파일로 지정한다. 홈에 프로필을 두고 `--user-data-dir`에 전달한다. Chromium 시작에 문제가 생기면 실제 오류를 확인하며 보안 옵션을 자동으로 끄지 않는다.

```bash
CHROMIUM_BIN="/실제/Chromium/실행파일"
Xvfb :99 -screen 0 1280x800x24 -nolisten tcp > /dev/null 2>&1 &
DISPLAY=:99 openbox > /dev/null 2>&1 &
DISPLAY=:99 "$CHROMIUM_BIN" --user-data-dir="$HOME/cloud-shell-browser/profile" --remote-debugging-address=127.0.0.1 --remote-debugging-port=9222 > /dev/null 2>&1 &
x11vnc -display :99 -localhost -nopw -forever -shared -nosel -rfbport 5900 > /dev/null 2>&1 &
websockify --web=/usr/share/novnc 127.0.0.1:6080 127.0.0.1:5900 > /dev/null 2>&1 &
```

포트 번호나 noVNC 경로가 다르면 실제 환경에 맞춘다. `-nosel`은 클립보드 브리지와 x11vnc 간의 중복 선택 동기화를 피하기 위한 신규 세션 설정이다. 새 프로세스가 각 포트에 실제로 떠 있는지 점검하고 실패 시 오류를 확인한다. 표준 출력 억제 때문에 원인을 못 찾으면 임시 테스트 로그를 만들되 개인 텍스트가 기록되지 않도록 주의한다.

매 세션 사용자가 요청한 명령을 먼저 실행한다.

```bash
cloudshell get-web-preview-url -p 8080
```

그 결과에서 이번 세션의 `https://` 출처만 확인해 `PREVIEW_ORIGIN`에 넣는다. 명령이 없거나 실패하면 성공한 것처럼 처리하지 말고 `cloudshell help`와 Google Cloud 웹 미리보기 UI를 확인한다. 브리지에 필요한 것은 경로·쿼리가 없는 정확한 출처다. 출력한 개인 주소는 다른 사람에게 공유하지 않는다.

```bash
PREVIEW_ORIGIN='https://이번-세션의-미리보기-호스트'
"$HOME/.venvs/cloud-shell-clipboard/bin/python" "$SKILL_DIR/scripts/bridge.py" \
  --origin "$PREVIEW_ORIGIN" --display :99 --upstream-port 6080 --port 8080
```

브리지는 포그라운드에서 실행되므로 별도 터미널을 사용한다. 미리보기 주소 뒤에 `/vnc.html?autoconnect=1&resize=scale`을 붙여 열고, noVNC 클립보드 패널의 `원격 화면에 붙여넣기` 버튼이 있는지 확인한다. 브리지가 종료되면 화면이 끊긴다. 정확한 미리보기 Origin 이외의 HTTP POST·WebSocket Origin을 허용하지 않으며 전송 텍스트를 로그에 기록하지 않는다.

## 3. 실제 검증

1. `curl -sS http://127.0.0.1:9222/json/version`으로 CDP가 켜져 있는지 확인한다. 기존 Chromium의 CDP와 화면이 일치하는지 별도 테스트용 탭을 열어 양쪽에서 확인하고 탭만 닫는다. WebSocket 주소는 공개하지 않는다.
2. 실제 Cloud Shell HTTPS 미리보기의 원격 화면에서 테스트 입력란을 클릭한다. noVNC 클립보드 보드에 직접 비밀이 아닌 한글과 영문을 붙여 넣고 **원격 화면에 붙여넣기**를 눌러 값이 정확한지 확인한다. 외부 프록시 호환성, 포커스, x11vnc 동기화 충돌을 따로 확인한다.
3. 별도 localhost 테스트를 원하면 원래 브리지를 종료하지 말고 테스트용 포트를 확보한다. `bridge.py --allow-local-test`는 정해진 localhost Origin을 위한 테스트 모드이며 프로덕션 Origin에 대한 추가 허용 설정이 아니다. localhost에 접속 가능한 브라우저에서 한글과 영문을 동일하게 검증한다. localhost 검증 성공이 HTTPS 미리보기 성공을 뜻하지 않는다.
4. `scripts/test_bridge.py`는 HTTP·WebSocket 출처 검증과 UTF-8 전달을 모의 객체로 검사한다. 실제 X11·noVNC·Cloud Shell 미리보기 테스트를 대체하지 않는다.

검증 결과는 localhost, 실제 미리보기, 원격 입력란에 대한 한글·영문 성공을 각각 보고한다. 재접속 후에는 홈의 프로필과 스크립트를 재사용하며 시스템 패키지 및 프로세스 상태를 다시 확인한다.
