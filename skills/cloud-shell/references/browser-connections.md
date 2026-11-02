# Cloud Shell 브라우저 연결과 검증

사용자가 안내만 원하면 아래 명령을 직접 실행하도록 안내한다. 기존 브라우저 프로필과 실행 중인 프로세스를 먼저 확인하고 재시작·삭제하지 않는다. 개인 접속 주소, 브라우저 디버깅 WebSocket URL, 인증 정보는 공유하거나 공개 저장소에 기록하지 않는다.

## Chromium: 기존 브라우저의 CDP

Cloud Shell에서 실행 중인 Chromium이 있으면 먼저 경로와 CDP 응답을 확인한다. Playwright에서 설치한 Chromium은 `~/.cache/ms-playwright/` 아래에 있을 수 있다. 해당 경로에 설치되지 않은 환경에는 이 예시를 일반 경로로 오인하지 않도록 한다.

```bash
find "$HOME/.cache/ms-playwright" -type f -name chrome -print 2>/dev/null
curl -sS http://127.0.0.1:9222/json/version
```

포트 9222는 흔한 예시일 뿐 실제 포트는 환경별로 확인한다. JSON의 `Browser` 및 `Protocol-Version` 응답은 CDP 엔드포인트의 존재를 의미하지만 실제 브라우저 제어 성공을 보장하지 않는다. `webSocketDebuggerUrl`을 공유하지 않는다. 브라우저 디버깅 포트는 인증된 세션과 데이터를 제어할 수 있으므로 외부에 공개하지 않는다.

기존 환경의 Playwright가 설치된 Python을 확인하고 다음 스크립트의 Python 경로와 포트를 실제 값으로 바꿔 실행한다. 새 임시 페이지를 열어 제목을 읽은 뒤 닫는다. 기존 브라우저를 종료하거나 기존 프로필을 변경하지 않는다.

```bash
/path/to/venv/bin/python - <<'PY'
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.new_page()
    try:
        page.goto("data:text/html,<title>CDP test OK</title>")
        print("페이지 제목:", page.title())
    finally:
        page.close()
PY
```

`페이지 제목: CDP test OK`가 나오면 실제 제어를 확인한 것이다. 이 명령은 기존 CDP를 찾아 연결하며 신규 브라우저를 설치하거나 CDP를 켜지 않는다. 기존 서버가 없으면 무작정 기존 프로세스를 종료하지 말고 사용자 환경과 요구에 맞는 별도의 브라우저·프로필 구성 후 검증한다. 위 연결 테스트는 한 Cloud Shell 세션의 Playwright Chromium에서 성공했으나 모든 환경에 대한 보장은 아니다.

## Firefox: Docker 화면

기존 컨테이너와 바인딩을 먼저 확인한다.

```bash
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Ports}}'
```

`cloud-firefox`가 없고 사용자가 설치를 원하면 SKILL.md의 Docker 명령을 안내한다. `127.0.0.1:3000->3000/tcp`를 확인한 후 Cloud Shell **웹 미리보기 → 포트 변경 → 3000**을 열고 사용자가 Firefox 화면이 보이는지 확인한다. 8080은 다른 서비스일 수 있다. 기본 예시는 컨테이너가 종료되면 저장한 프로필·파일이 사라진다.

`Waiting for stream`이 나오면 `docker logs --tail 80 cloud-firefox`로 시작과 연결 상태를 확인한다. 한 세션에서는 Selkies 클라이언트 연결과 영상 캡처가 시작된 상태에서 미리보기 탭을 하나만 남기고 새로고침한 후 Firefox 화면이 보였다. 같은 조치가 모든 환경에서 해결됨을 보장하지 않는다. 하드웨어 인코더가 없어 소프트웨어로 전환한 로그만으로 실패라고 단정하지 않는다. 계속 실패하면 로그·실제 화면과 [스트리밍 프록시 요구사항](https://docs.linuxserver.io/selkies/user-guide/reverse-proxy/)을 검토한다.

## Firefox: BiDi는 별도로 확인

현재 Firefox는 CDP 대신 WebDriver BiDi를 사용한다. [Mozilla 원격 프로토콜](https://firefox-source-docs.mozilla.org/remote/Prefs.html), [BiDi 연결](https://developer.mozilla.org/en-US/docs/Web/WebDriver/How_to/Create_BiDi_connection)을 참고한다. 컨테이너에서 실행 파일, 버전, 프로세스를 확인하는 예:

```bash
docker exec cloud-firefox sh -c 'command -v firefox; firefox --version; pgrep -a firefox'
```

Firefox 159 실행과 화면 표시는 한 환경에서 확인했지만, **BiDi 연결과 제어는 아직 검증하지 않았다.** 실제 테스트 때는 기존 GUI를 보존하고 별도의 임시 프로필·로컬 전용 포트와 적절한 클라이언트를 마련해 핸드셰이크와 페이지 제어를 각각 확인한다. 컨테이너 내부 루프백은 호스트의 루프백과 다르며, 단순히 포트를 지정했다고 연결이 증명되지는 않는다. 원격 제어 포트를 공개하지 않는다. Docker Chromium도 별도 환경에서 설치·실행·CDP·화면 표시를 확인하기 전까지 미검증으로 보고한다.
