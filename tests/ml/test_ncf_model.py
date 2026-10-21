"""Pruebas unitarias para el modelo PyTorch Neural Collaborative Filtering."""

import torch

from app.infrastructure.ml.neural_cf_model import NeuralCollaborativeFiltering


def test_ncf_forward_pass_shape_and_bounds() -> None:
    """Verifica que el modelo NCF retorne probabilidades acotadas en [0.0, 1.0]."""
    torch.manual_seed(42)
    model = NeuralCollaborativeFiltering(
        num_users=100,
        num_exercises=50,
        embedding_dim=8,
        mlp_hidden_layers=[16, 8],
    )
    model.eval()

    users = torch.tensor([0, 10, 25, 99], dtype=torch.long)
    exercises = torch.tensor([5, 12, 45, 0], dtype=torch.long)

    with torch.no_grad():
        preds = model(users, exercises)

    assert preds.shape == (4, 1)
    assert torch.all(preds >= 0.0)
    assert torch.all(preds <= 1.0)


def test_ncf_training_step() -> None:
    """Verifica que el modelo NCF sea diferenciable y pueda calcular gradientes con BCELoss."""
    model = NeuralCollaborativeFiltering(
        num_users=50,
        num_exercises=20,
        embedding_dim=4,
        mlp_hidden_layers=[8],
    )
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    criterion = torch.nn.BCELoss()

    users = torch.tensor([1, 2, 3], dtype=torch.long)
    exercises = torch.tensor([4, 5, 6], dtype=torch.long)
    targets = torch.tensor([[1.0], [0.0], [1.0]], dtype=torch.float32)

    optimizer.zero_grad()
    outputs = model(users, exercises)
    loss = criterion(outputs, targets)
    loss.backward()

    # Verificar que los gradientes no sean nulos
    assert model.prediction_layer.weight.grad is not None
    optimizer.step()
    assert loss.item() > 0.0
