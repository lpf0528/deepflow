from langchain.chat_models import BaseChatModel
from src.config.app_config import get_app_config
from src.config.tracing_config import is_tracing_enabled, get_tracing_config
from src.reflection.resolvers import resolve_class


def create_chat_model(name: str | None = None, thinking_enabled: bool = True, **kwargs) -> BaseChatModel:
    """创建聊天模型
    """
    config = get_app_config()
    name = name or config.models[0].name

    # 根据名字获取模型配置
    model_config = config.get_model_config(name)
    if model_config is None:
        raise ValueError(f"模型配置不存在：{name}")

    # 获取模型类
    model_class = resolve_class(model_config.use, BaseChatModel)
    # 从配置中提取模型参数，排除name和use和None值
    model_settings_from_config = model_config.model_dump(exclude_none=True,
                                                         exclude={"name", "use"})
    if thinking_enabled and model_config.when_thinking_enabled is not None:
        if not model_config.supports_thinking:
            raise ValueError(f"模型 {name} 不支持思考模式")
        # 合并思考模式下的参数
        model_settings_from_config.update(model_config.when_thinking_enabled)
    # 合并其他参数
    model_settings_from_config.update(kwargs)
    # 如果思考模式禁用，且配置了思考模式参数，设置思考模式为disabled
    if not thinking_enabled and model_config.when_thinking_enabled and model_config.when_thinking_enabled.get("extra_body", {}).get("thinking", {}).get("type"):
        kwargs.update({"extra_body": {"thinking": {"type": "disabled"}}})
        kwargs.update({"reasoning_effort": "minimal"})
    # 如果模型不支持 reasoning_effort，设置为 None
    # if not model_config.supports_reasoning_effort:
    #     kwargs.update({"reasoning_effort": None})

    model_instance = model_class(**kwargs, **model_settings_from_config)
    if is_tracing_enabled():
        try:
            from langchain_core.tracers.langchain import LangChainTracer
            tracing_config = get_tracing_config()
            tracer = LangChainTracer(
                project_name=tracing_config.project
            )
            # 合并已有的回调
            existing_callbacks = model_instance.callbacks or []
            # LangSmith追踪已附加到模型‘{name}’的回调
            model_instance.callbacks = [*existing_callbacks, tracer]
        except Exception as e:
            print(f"添加LangSmith追踪回调失败：{e}")
    return model_instance
