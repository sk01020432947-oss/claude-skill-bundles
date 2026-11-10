---
name: kr-gallery-command
description: 한국어 예제 갤러리(44개) 지도와 "참고 코드 + 정확 명령" 요청 틀. 새 리모션 장면을 처음부터 짜기 전에 가장 가까운 예제를 고르고, 한글 글꼴을 고정할 때 읽는다.
metadata:
  tags: korean, gallery, prompt, fonts, pretendard
  source: CONNECT AI LAB 영상(2026-10-09, https://www.youtube.com/watch?v=7NBu5IW_2Xw) · https://www.aicitybuilders.com/remotion (2026-10-09 확인, Remotion 4.0.529 기준)
---

# 한국어 예제 갤러리 + 정확 명령

## 1. 처음부터 짜지 말고 가장 가까운 예제부터
갤러리: https://www.aicitybuilders.com/remotion — 결과 영상 + 코드(복사 버튼). 코드를 `src/Scene.tsx`에 붙이고 이미지 주소·글자만 바꾼다.

| 번호 | 범주 | 예제 |
|---|---|---|
| 51–57 | 제품 광고 | 히어로 등장 · 제품 캐러셀 · 특징 콜아웃 · 세로 쇼츠 광고(1080×1920) · 가격·할인 배지 · 캐릭터가 소개하는 광고 · 라인업 3D 쇼케이스 |
| 41–47 | 캐릭터 PNG | 등장+말풍선 · 살아 있는 대기 동작 · 점프 이동 · 패럴랙스 장면 · 강의 프로필 카드 · 캐릭터 군단 연결 · 스티커 효과 |
| 01a–c | 기본기 | 프레임→값(interpolate·spring) · Sequence/Series/Loop/Freeze · Img/OffthreadVideo/Audio |
| 02–07 | 전환·효과 | transitions · light-leaks · starburst · effects(기초/강의 레시피) · motion-blur · noise |
| 08–11 | 움직임·도형 | paths · shapes · svg-3d-engine · animation-utils(interpolateStyles) |
| 12–17 | 글자·자막 | rough-notation · rounded-text-box · captions(쇼츠식) · layout-utils(글자 맞춤) · google-fonts · fonts(Pretendard) |
| 18–24, 27 | 미디어·소리 | animated-emoji · mac-cursors · gsap · lottie · gif · media-utils(오디오 비주얼라이저) · sfx · media |
| 25, 31 | 3D·분석 | three(R3F) · media-parser |

새 패키지는 공식 `remotion-markup`(effects·light-leaks·motion-blur·sfx 등)을 먼저 보고, 거기 없는 것(starburst·rough-notation·rounded-text-box·noise·gsap·mac-cursors·animated-emoji·svg-3d-engine)은 갤러리 예제 코드를 참고한다.

## 2. 갤러리의 공용 파일 2개 (처음 한 번)
`src/Root.tsx`
```tsx
import {Composition} from 'remotion';
import {Scene} from './Scene';
export const RemotionRoot = () => (
  <Composition id="Scene" component={Scene}
    durationInFrames={180} fps={30} width={1280} height={720} />
);
```
`src/font.ts` — 한글은 Pretendard로 고정(렌더 환경이 바뀌어도 같은 글꼴)
```ts
import {loadFont} from '@remotion/fonts';
export const FONT = 'Pretendard';
loadFont({family: FONT, url: 'https://cdn.jsdelivr.net/npm/pretendard@1.3.9/dist/web/variable/woff2/PretendardVariable.woff2', weight: '45 920', format: 'woff2'});
```
오프라인 렌더면 woff2를 `public/`에 두고 `staticFile()`로 바꾼다.

## 3. 요청 틀 (영상 14:00, 20:00 그대로)
"해 줘"가 아니라 재료와 코드를 주고 시킨다. 영상에서 같은 틀을 Opus 5.5·GPT-6.1 Sol·Gemini 3.8 Flash에 넣었을 때 결과 차이가 작았다(화자 평가, 2회 비교).
```
<무엇을> <몇 초> 만들어 줘. (예: 첨부된 제품 이미지 2개로 20초 홍보 영상)
:: 배경색 <값>
:: 조명/색 <값>
:: 글자 <정확한 문구>, 글꼴 src/font.ts의 FONT
:: 이미지 <폴더 경로 또는 파일> (누끼가 필요하면 그렇게 말한다)
:: 참고 코드
<갤러리에서 복사한 코드 붙여넣기>
:: 추가 요청 <바꿀 것 / 지울 것>
:: 모션그래픽 오픈소스 사용: remotion
```
수정은 "<프레임 또는 초> · <무엇> · <어떻게> · <무엇은 그대로>"로 한 부분만. 전체 재생성 금지.

## 4. 라이선스
설명란 정정 문구(2026-10-09): 개인·직원 3명 이하 회사·비영리 무료, 4명 이상 회사는 회사 라이선스(remotion.pro). 영상 속 "5인 미만" 발언은 틀린 것으로 정정됨. 실제 조건은 https://www.remotion.dev/docs/license 에서 다시 확인한다.
