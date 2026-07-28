# 블로그 자동화 시스템 — korea-it-quote

## 프로젝트 개요
키워드 하나로 리서치 → 팩트체크 → 구조설계 → 초안 → 검수 → 발행까지 6단계 자동 실행.
발행된 글은 `blog-posts/` 폴더에 저장되고 GitHub Pages 블로그 탭에 자동으로 표시된다.

## 디렉토리 구조
```
korea-it-quote/
├── blog-posts/
│   ├── index.json        ← 발행된 글 목록 (블로그 탭이 이 파일을 읽음)
│   └── {파일명}.md       ← 개별 글 파일
├── context/              ← 톤·가독성·SEO·금지표현
├── drafts/               ← 작업 중간 파일 (git 제외)
└── .claude/
    ├── agents/           ← 6개 서브에이전트
    └── skills/           ← blog-pipeline 스킬
```

## 핵심 규칙 (항상 적용)
1. `context/` 폴더의 4개 파일을 **항상** 먼저 읽고 시작한다
2. 오늘 날짜 기준 최신 정보만 사용한다
3. 팩트체커가 REJECTED 처리한 내용은 글에 포함하지 않는다
4. 발행(git push) 전 반드시 사용자 확인을 받는다
5. 최종본은 `C:\Users\IT-대구\Desktop\블로그 작성기` 폴더에도 `{YYYY-MM-DD}_{제목}.txt` 형식으로 저장한다 (GitHub Pages 접속이 안 될 때를 위한 로컬 백업용)

## 에이전트 파이프라인
```
키워드 입력
  → [researcher]   웹 리서치 (haiku, 저비용)
  → [fact-checker] 사실 검증 (sonnet)
  → [planner]      글 구조 설계 (sonnet)
  → [writer]       초안 작성 (sonnet)
  → [reviewer]     품질 검수 (sonnet)
  → [publisher]    blog-posts/ 저장 + index.json 갱신 + git push
```

## 발행 후 결과
GitHub Pages 블로그 탭(https://chan63078-dot.github.io/korea-it-quote/)의
"Claude 발행 글" 섹션에 자동으로 글이 표시된다.
