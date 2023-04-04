#!/bin/bash
curl https://api.openai.com/v1/completions \
  -H "Content-Type: application/json" \
  -H "OpenAI-Organization: org-NdwlPI1zbabscm4v19upumJn" \
  -H "Authorization: Bearer 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" \
  -d '{
    "model": "text-davinci-003",
    "prompt": "Say this is a test",
    "max_tokens": 7,
    "temperature": 0
  }'