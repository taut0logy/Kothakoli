export const AVAILABLE_MODELS = [
  "gemini-2.0-flash-exp",
  "gemini-1.5-pro",
  "gemini-1.5-pro-vision",
  "gemini-1.5-flash-latest"
]

export const AVAILABLE_VOICE_MODELS = [
  "gemini-2.0-flash-exp",
  "gemini-1.5-pro",
]

export const AVAILABLE_VISION_MODELS = [
  "gemini-2.0-flash-exp",
  "gemini-1.5-pro",
  "gemini-1.5-pro-vision",
]

export const MODEL_CONFIGS = {
  "gemini-1.5-pro": {
    temperature: 0.7,
    top_p: 0.9,
    top_k: 40,
    max_output_tokens: 2048,
  },
  "gemini-1.5-pro-vision": {
    temperature: 0.7,
    top_p: 0.9,
    top_k: 40,
    max_output_tokens: 2048,
  },
  "gemini-1.5-flash-latest": {
    temperature: 0.7,
    top_p: 0.9,
    top_k: 40,
    max_output_tokens: 1024,
  },
  "gemini-2.0-flash-exp": {
    temperature: 0.7,
    top_p: 0.9,
    top_k: 40,
    max_output_tokens: 1024,
  }
} 