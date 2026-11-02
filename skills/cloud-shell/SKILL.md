---
name: cloud-shell
description: Use when setting up or troubleshooting Google Cloud Shell with Codex CLI, tmux, a visible Linux browser, disconnections, web preview, noVNC or CDP.
---

# Cloud Shell 사용 안내

Google Cloud Shell에서 Linux와 Codex를 사용하려는 사람을 돕는다. 사용자가 설명만 원하면 명령과 결과 확인 방법만 제공하며 브라우저, 터미널 또는 계정을 직접 조작하지 않는다. 명시적으로 허용한 후속 작업은 그 범위에서 진행한다. 자격 증명, 일회용 인증 코드, 계정명, 세션 ID와 개인 미리보기 주소는 예시나 공개 산출물에 저장하지 않는다.

## 기본 순서: Cloud Shell → 터미널 → tmux → Codex

1. [Cloud Shell](https://shell.cloud.google.com/)에 접속하고 로그인해 터미널을 연다. 서비스 접근 및 최초 승인 안내는 사용자가 직접 진행하도록 설명한다.
2. 편집기 화면이 필요 없으면 상단 툴바의 연필 모양 **편집기 닫기**를 클릭하도록 안내해 터미널을 넓힌다. 편집기와 터미널 닫기 버튼을 혼동하지 않는다.
3. `tmux -V`로 버전을 확인한다. 최신 버전을 원하는 경우 아래 tmux 절의 공식 릴리스와 홈 디렉터리 설치 절차를 사용한다. 버전 번호와 사용 중인 서버를 구분한다. 이미 tmux에서 실행 중이라면 새 세션을 억지로 중첩하지 않는다.
4. `codex --version`과 `codex login status`로 설치와 로그인 상태를 확인한다. 설치·로그인이 필요하면 아래 Codex 절에 따라 진행한 뒤 `codex`를 실행한다. 기존 대화를 이어갈 때는 `codex resume`을 사용한다.

## 환경과 비용

- Cloud Shell 자체는 이미 Linux 환경이며 기본 모드는 홈 디렉터리를 세션 간 보존하지만 VM과 홈 밖의 변경은 임시다. 비활성 시간과 최대 세션 시간 제한은 [Google 공식 문서](https://docs.cloud.google.com/shell/docs/quotas-limits)를 확인한다. 돌아가는 작업을 24시간 보장하지 않는다.
- 별도 Compute Engine VM은 결제 계정이 필요하며 요금이 발생할 수 있다. 무료 등급은 특정 리전·머신 유형·사용 한도에만 적용된다. 외부 IP와 네트워크 등 별도 과금도 확인한다. 서울 리전은 무료 VM 대상이라고 안내하지 않는다. 최신 조건은 [무료 등급](https://docs.cloud.google.com/free/docs/free-cloud-features)을 확인한다.

## Codex 설치와 로그인

홈에 설치해 기본 Cloud Shell에서 보존하려면 공식 npm 패키지를 사용한다. 우선 Node.js/npm과 기존 설치를 확인한다. 설치 위치를 바꿀 필요가 없다면 기존 설정을 보존한다.

```bash
npm install -g --prefix "$HOME/.local" @openai/codex
"$HOME/.local/bin/codex" --version
```

`codex`가 PATH에 있으면 `codex`로 실행하고, 없으면 `"$HOME/.local/bin/codex"`를 사용한다. 원격 환경에서 일반 로그인 콜백이 작동하지 않으면 `codex login --device-auth`를 안내하고 사용자가 자기 브라우저에서 코드를 입력하게 한다. PATH에 없다면 `"$HOME/.local/bin/codex" login --device-auth`를 사용한다. 설정에서 기기 코드 로그인을 켜야 할 수 있다. ChatGPT 계정의 사용 권한·한도와 API 키의 별도 사용량 과금을 구분한다. [Codex 설치](https://learn.chatgpt.com/docs/codex/cli), [원격 로그인](https://learn.chatgpt.com/docs/auth#login-on-headless-devices).

연결이 끊긴 경우 출력된 `codex resume <세션-ID>`를 우선 사용하거나 `codex resume`으로 선택한다. `Server is draining`은 일시적인 서버 교체·종료 과정일 수 있으므로 재연결하고 계속 실패하면 실제 오류를 확인한다. 작업이 반드시 계속 실행 중이라고 단정하지 않는다. `--yolo`는 연결 복구에 필요하지 않다.

## tmux

Cloud Shell은 기본적으로 tmux를 사용한다. `tmux -V`는 설치된 클라이언트 버전을 확인한다. `sessions should be nested with care`는 이미 tmux 안에서 새 세션을 열려는 상황이며 설치 오류가 아니다. 기존 세션과 작업을 보존하고 무작정 `TMUX`를 지우거나 서버를 종료하지 않는다. VM이 종료되면 tmux와 실행 중 프로세스도 종료된다. [Cloud Shell tmux 안내](https://docs.cloud.google.com/shell/docs/configuring-cloud-shell#tmux-support).

최신 tmux 설치 요청에는 [공식 릴리스](https://github.com/tmux/tmux/releases/latest)와 [빌드 안내](https://github.com/tmux/tmux/wiki/Installing)를 확인하고 홈의 별도 경로에 설치하는 방법을 제공한다. 시스템 빌드 의존성은 임시 환경에서 사라질 수 있으며 새 바이너리 설치가 현재 실행 중인 기존 서버를 자동 업그레이드하지 않음을 알린다.

Ubuntu/Debian에서 최신 안정판의 정확한 버전을 공식 릴리스에서 확인한 뒤 아래 예시의 `VERSION`을 바꿔 한 단계씩 제공한다. 다운로드·설정·빌드가 실패하면 중단하고 오류를 확인한다.

```bash
sudo apt update
sudo apt install -y build-essential libevent-dev libncurses-dev bison pkg-config curl
VERSION=3.8
cd /tmp
curl -fLO "https://github.com/tmux/tmux/releases/download/$VERSION/tmux-$VERSION.tar.gz"
tar -xzf "tmux-$VERSION.tar.gz"
cd "tmux-$VERSION"
./configure --prefix="$HOME/.local" && make && make install
"$HOME/.local/bin/tmux" -V
cd ~
```

예시 버전은 시간이 지나면 바뀔 수 있다. 명령으로 설치된 바이너리만 검증하고 기존 Cloud Shell 서버 버전까지 바뀌었다고 주장하지 않는다.

사용자가 새 버전의 tmux를 실제로 쓰길 원하고 기존 Cloud Shell tmux 안에 있는 경우에만, 별도의 소켓을 명시해 중첩 세션을 만들 수 있다. 기존 세션을 유지하며 버전이 다른 서버 간 호환성을 가정하지 않는다.

```bash
env -u TMUX "$HOME/.local/bin/tmux" -L codex-modern new -s codex-work
```

새 세션 안에서 `codex`를 실행한다. 다시 연결할 때는 `env -u TMUX "$HOME/.local/bin/tmux" -L codex-modern attach -t codex-work`를 사용한다. 두 tmux가 중첩되므로 단축키 입력은 겉 세션과 안쪽 세션을 구분해야 한다. Cloud Shell VM이 종료되면 두 서버 모두 사라진다. 기존 tmux만으로 충분하다면 중첩하지 않는다.

## 눈에 보이는 브라우저와 CDP

Cloud Shell은 기본적으로 터미널 환경이다. 사용 중인 브라우저·noVNC가 이미 있으면 새 설치보다 기존 상태와 웹 미리보기 포트를 먼저 확인한다. 실제 확인한 주소만 전달하고 이전 세션의 주소, 포트 또는 파일 경로가 앞으로도 유효하다고 가정하지 않는다. CDP는 해당 환경 내부 주소와 인증 경계에 주의하고 인터넷에 공개하지 않는다. 화면을 볼 수 있다는 것과 Codex가 CDP로 제어할 수 있다는 것은 별개다.

대안으로 Firefox GUI 컨테이너를 Cloud Shell의 인증된 HTTPS 웹 미리보기 뒤에 둘 수 있다. [Firefox 이미지](https://docs.linuxserver.io/images/docker-firefox/)의 HTTP 포트는 역방향 프록시 뒤에서만 사용한다. 환경별 호환성은 검증 전까지 보장하지 않는다.

```bash
docker run -d --name cloud-firefox --rm --shm-size=1gb \
  -p 127.0.0.1:3000:3000 lscr.io/linuxserver/firefox:latest
```

웹 미리보기에서 포트 3000을 선택한다. 종료는 `docker stop cloud-firefox`. 이 예시에는 영구 볼륨이 없으므로 컨테이너 종료 시 브라우저 데이터가 사라진다. 포트 충돌이나 기존 이름이 있다면 먼저 상태를 확인한다. [Cloud Shell 웹 미리보기](https://docs.cloud.google.com/shell/docs/using-web-preview)는 사용자 계정에 접근을 제한하지만 미리보기 주소와 인증 정보는 공유하지 않는다.

Firefox·Chromium 브라우저와 WebDriver의 설치 또는 검증을 요청하면 [브라우저 및 드라이버 검증](references/browser-drivers.md)을 읽는다. 제공된 검증 스크립트는 각 브라우저가 실제로 시작해 지정된 로컬 테스트 페이지의 제목을 읽는지 확인한다. Selenium의 자동 다운로드가 성공하거나 GUI가 연결되었다고 사전에 단정하지 않는다.
