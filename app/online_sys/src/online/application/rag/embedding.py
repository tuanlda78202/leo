from typing import Literal, Union

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings

EmbeddingModelType = Literal["openai", "huggingface", "google"]
EmbeddingsModel = Union[
    OpenAIEmbeddings, HuggingFaceEmbeddings, GoogleGenerativeAIEmbeddings
]


def get_embedding_model(
    model_id: str,
    model_type: EmbeddingModelType = "huggingface",
    device: str = "cpu",
) -> EmbeddingsModel:
    """Gets an instance of the configured embedding model.

    The function returns either an OpenAI or HuggingFace embedding model based on the
    provided model type.

    Args:
        model_id (str): The ID/name of the embedding model to use
        model_type (EmbeddingModelType): The type of embedding model to use.
            Must be either "openai" or "huggingface". Defaults to "huggingface"
        device (str): The device to use for the embedding model. Defaults to "cpu"

    Returns:
        EmbeddingsModel: An embedding model instance based on the configuration settings

    Raises:
        ValueError: If model_type is not "openai" or "huggingface"
    """

    if model_type == "openai":
        return get_openai_embedding_model(model_id)
    elif model_type == "google":
        return get_gemini_embedding_model(model_id)
    elif model_type == "huggingface":
        return get_huggingface_embedding_model(model_id, device)
    else:
        raise ValueError(f"Invalid embedding model type: {model_type}")


def get_openai_embedding_model(model_id: str) -> OpenAIEmbeddings:
    """Gets an OpenAI embedding model instance.

    Args:
        model_id (str): The ID/name of the OpenAI embedding model to use

    Returns:
        OpenAIEmbeddings: A configured OpenAI embeddings model instance with
            special token handling enabled
    """
    return OpenAIEmbeddings(
        model=model_id,
        allowed_special={"<|endoftext|>"},
    )


def get_gemini_embedding_model(
    model_id: str,
) -> GoogleGenerativeAIEmbeddings:
    """Gets a Google Gemini embedding model instance.

    Args:
        model_id (str): The ID/name of the Google Gemini embedding model to use

    Returns:
        GoogleGenerativeAIEmbeddings: A configured Google Gemini embeddings model instance
    """
    return GoogleGenerativeAIEmbeddings(
        model=model_id,
    )


def get_huggingface_embedding_model(
    model_id: str, device: str
) -> HuggingFaceEmbeddings:
    """Gets a HuggingFace embedding model instance.

    Args:
        model_id (str): The ID/name of the HuggingFace embedding model to use
        device (str): The compute device to run the model on (e.g. "cpu", "cuda")

    Returns:
        HuggingFaceEmbeddings: A configured HuggingFace embeddings model instance
            with remote code trust enabled and embedding normalization disabled
    """
    return HuggingFaceEmbeddings(
        model_name=model_id,
        model_kwargs={"device": device, "trust_remote_code": True},
        encode_kwargs={"normalize_embeddings": False},
    )
