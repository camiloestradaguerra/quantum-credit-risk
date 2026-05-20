from qiskit.circuit.library import ZZFeatureMap
from qiskit_machine_learning.kernels import FidelityQuantumKernel
import numpy as np

# Create simple feature map
feature_map = ZZFeatureMap(feature_dimension=8, reps=2)

# Try to create FidelityQuantumKernel without fidelity
try:
    kernel = FidelityQuantumKernel(feature_map=feature_map)
    print("✓ FidelityQuantumKernel created successfully!")
    print(f"Kernel: {kernel}")
    
    # Try with small data
    X_train = np.random.rand(10, 8) * 2 * np.pi
    print(f"\nAttempting to evaluate kernel on {X_train.shape[0]} samples...")
    K = kernel.evaluate(X_train)
    print(f"✓ Kernel matrix computed: {K.shape}")
    print(f"Kernel values - min: {K.min():.4f}, max: {K.max():.4f}")
    
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
