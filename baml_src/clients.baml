// Learn more about clients at https://docs.boundaryml.com/docs/snippets/clients/overview

client<llm> OpenAIo1 {
  provider openai
  options {
    model "o1"
    reasoning_effort "high"
    temperature 1
    api_key env.OPENAI_API_KEY

  }
}

client<llm> OpenAIo1Mini {
  provider openai
  options {
    model "o1-mini"
    temperature 1
    api_key env.OPENAI_API_KEY

  }

}

client<llm> OpenAIo3Mini {
  provider openai
  retry_policy Exponential

  options {
    reasoning_effort "high"
    model "o3-mini"
    temperature 1
    api_key env.OPENAI_API_KEY
  }
}

client<llm> OpenAIGPT4o {
  provider openai
  retry_policy Exponential

  options {
    temperature 1
    model "gpt-4o"
    api_key env.OPENAI_API_KEY

  }
}


client<llm> DeepseekReasoner {
  provider openai-generic
  options {
    model deepseek-ai/DeepSeek-R1
    api_key env.DEEPSEEK_API_KEY
    base_url "https://api.hyperbolic.xyz/v1/"
    default_role "user"
    temperature 1

  }
}


client<llm> AnthropicSonnet {
  provider anthropic
  options {
    model "claude-3-5-sonnet-latest"
    api_key env.ANTHROPIC_API_KEY
    temperature 1
  }

}


// https://docs.boundaryml.com/docs/snippets/clients/retry
retry_policy Constant {
  max_retries 3
  // Strategy is optional
  strategy {
    type constant_delay
    delay_ms 200
  }
}

retry_policy Exponential {
  max_retries 2
  // Strategy is optional
  strategy {
    type exponential_backoff
    delay_ms 300
    mutliplier 1.5
    max_delay_ms 10000
  }
}