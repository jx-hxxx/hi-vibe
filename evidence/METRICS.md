# Metrics evidence

포트폴리오와 기술 의사결정에 다시 사용할 정량 성과의 근거입니다. 같은 조건에서
재현할 수 있도록 명령·환경·표본을 함께 남깁니다.

## write-gate 상시 로딩 지침 축소

- 측정일: 2026-09-11 11:37
- 지표: `skills/write-gate/SKILL.md` 줄 수
- 변경 전: 361줄
- 변경 후: 70줄
- 개선율: `(361 - 70) / 361 × 100 = 80.6%` 감소
- 측정 명령: `wc -l skills/write-gate/SKILL.md`
- 측정 환경: macOS, 동일 저장소·동일 `wc` 명령
- 표본: 변경 전·후 파일 각 1회
- 관련 커밋: 변경 기준 HEAD `17af71e`; v0.52.0 작업 트리
- 원본 결과: `evidence/raw/2026-09-11-write-gate-before.txt`, `evidence/raw/2026-09-11-write-gate-after.txt`
- 한계: 줄 수 감소를 측정한 결과이며 실제 모델 토큰 사용량은 측정하지 않음
