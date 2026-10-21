"""Implementación del modelo Neural Collaborative Filtering (NCF) en PyTorch."""

import torch
import torch.nn as nn


class NeuralCollaborativeFiltering(nn.Module):
    """Arquitectura neuronal híbrida combinando GMF (Generalized Matrix Factorization) y MLP."""

    def __init__(
        self,
        num_users: int = 1000,
        num_exercises: int = 60,
        embedding_dim: int = 16,
        mlp_hidden_layers: list[int] | None = None,
    ) -> None:
        """Inicializa las capas de embeddings y perceptrón multicapa."""
        super().__init__()
        if mlp_hidden_layers is None:
            mlp_hidden_layers = [32, 16, 8]

        # Embeddings de GMF
        self.gmf_user_embed = nn.Embedding(num_users, embedding_dim)
        self.gmf_exercise_embed = nn.Embedding(num_exercises, embedding_dim)

        # Embeddings de MLP
        self.mlp_user_embed = nn.Embedding(num_users, embedding_dim)
        self.mlp_exercise_embed = nn.Embedding(num_exercises, embedding_dim)

        # Capas densas de MLP
        mlp_layers: list[nn.Module] = []
        in_dim = embedding_dim * 2
        for h_dim in mlp_hidden_layers:
            mlp_layers.append(nn.Linear(in_dim, h_dim))
            mlp_layers.append(nn.ReLU())
            mlp_layers.append(nn.Dropout(p=0.1))
            in_dim = h_dim

        self.mlp_network = nn.Sequential(*mlp_layers)

        # Capa de predicción final (fusión de GMF + MLP)
        final_in_dim = embedding_dim + mlp_hidden_layers[-1]
        self.prediction_layer = nn.Linear(final_in_dim, 1)

    def forward(self, user_indices: torch.Tensor, exercise_indices: torch.Tensor) -> torch.Tensor:
        """Paso hacia adelante del modelo NCF.

        Args:
            user_indices: Tensor con los índices de usuario.
            exercise_indices: Tensor con los índices de ejercicio.

        Returns:
            Tensor con afinidad predicha en el rango [0.0, 1.0].
        """
        # Rama GMF
        gmf_u = self.gmf_user_embed(user_indices)
        gmf_e = self.gmf_exercise_embed(exercise_indices)
        gmf_vector = gmf_u * gmf_e

        # Rama MLP
        mlp_u = self.mlp_user_embed(user_indices)
        mlp_e = self.mlp_exercise_embed(exercise_indices)
        mlp_vector = torch.cat([mlp_u, mlp_e], dim=-1)
        mlp_out = self.mlp_network(mlp_vector)

        # Fusión
        fusion = torch.cat([gmf_vector, mlp_out], dim=-1)
        logits = self.prediction_layer(fusion)
        return torch.sigmoid(logits)
