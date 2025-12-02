import logging
from typing import Dict, Any

from ..state import State
from langchain_core.runnables import RunnableConfig
from ..utils import get_store
from ..configuration import DEFAULT_MEMORY_CONFIGS

logger = logging.getLogger(__name__)


async def load_memory_step(state: State, config: RunnableConfig) -> Dict[str, Any]:
    """
    Carrega memórias relevantes do armazenamento persistente (PostgreSQL)
    para cada schema definido.
    """
    logger.info("Iniciando carregamento de memórias.")
    user_id = config.get("configurable", {}).get("user_id")

    loaded_memories: Dict[str, Any] = {}

    if user_id:
        logger.info(
            f"Buscando memórias para user_id: {user_id} para schemas definidos."
        )
        try:
            async with await get_store() as store:
                for schema in DEFAULT_MEMORY_CONFIGS:
                    if schema.update_mode == "patch":
                        namespace = (user_id, "user_states")
                        key = schema.name
                        memory_item = await store.aget(namespace, key)
                        if memory_item:
                            loaded_memories[schema.name] = memory_item.value
                            logger.info(
                                f"Memória '{schema.name}' (patch) carregada para user_id: {user_id}."
                            )
                        else:
                            logger.info(
                                f"Nenhuma memória '{schema.name}' (patch) encontrada para user_id: {user_id}."
                            )
                    elif schema.update_mode == "insert":
                        namespace = (user_id, "events", schema.name)
                        insert_memories = await store.asearch(namespace, limit=5)
                        if insert_memories:
                            loaded_memories[schema.name] = [
                                item.value for item in insert_memories
                            ]
                            logger.info(
                                f"{len(insert_memories)} memórias '{schema.name}' (insert) carregadas para user_id: {user_id}."
                            )
                        else:
                            loaded_memories[schema.name] = []
                            logger.info(
                                f"Nenhuma memória '{schema.name}' (insert) encontrada para user_id: {user_id}."
                            )

            if loaded_memories:
                loaded_schemas = list(loaded_memories.keys())
                logger.info(
                    f"Carregamento de memórias concluído para user_id: {user_id}. Schemas carregados: {loaded_schemas}. Conteúdo: {str(loaded_memories)[:200]}"
                )
                logger.info(loaded_memories.get("User"))
            else:
                logger.info(
                    f"Nenhuma memória encontrada para user_id: {user_id} após verificar todos os schemas."
                )

        except Exception as e:
            logger.error(
                f"Erro ao carregar memórias para user_id: {user_id}. Erro: {e}",
                exc_info=True,
            )
            loaded_memories = {}
    else:
        logger.warning(
            "Nenhum user_id ou thread_id encontrado no estado para carregar memórias."
        )
        loaded_memories = {}

    return {"loaded_memories": loaded_memories, "user_id": user_id}
