"""
Model Loading Service (Step 3)

Singleton that loads all ML artifacts ONCE at application startup.

Why Singleton?
- Our trained_model.joblib is 1.5MB. Loading it per-request would be catastrophic.
- The preprocessor contains fitted StandardScaler parameters (mean, variance).
  Loading it per-request would waste ~50ms of disk I/O every time.
- In production Kubernetes, the readiness probe checks if this service is ready.
  If the model hasn't loaded, the pod is marked "not ready" and receives no traffic.
"""
import os
import json
import hashlib
import logging
import joblib
import pandas as pd

logger = logging.getLogger("ecopackai")


class ModelService:
    """Singleton service that owns the ML model lifecycle."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def load(self, artifacts_dir: str, processed_dir: str) -> None:
        """Load all production artifacts from disk.
        
        Args:
            artifacts_dir: Path to model, preprocessor, and metadata files.
            processed_dir: Path to processed materials CSV.
        """
        if self._initialized:
            logger.info("ModelService already initialized. Skipping reload.")
            return
        
        logger.info(f"Loading ML artifacts from {artifacts_dir}...")
        
        # Load model
        model_path = os.path.join(artifacts_dir, 'trained_model.joblib')
        self.model = joblib.load(model_path)
        logger.info("Trained model loaded.")
        
        # Load preprocessor
        self.preprocessor = joblib.load(
            os.path.join(artifacts_dir, 'preprocessor.joblib')
        )
        logger.info("Preprocessor loaded.")
        
        # Load materials database
        self.materials = pd.read_csv(
            os.path.join(processed_dir, 'processed_materials.csv')
        )
        logger.info(f"Materials loaded: {len(self.materials)} materials available.")
        
        # Load registry metadata
        registry_path = os.path.join(artifacts_dir, 'model_registry.json')
        with open(registry_path, 'r') as f:
            self.registry = json.load(f)
        
        # Load metrics
        metrics_path = os.path.join(artifacts_dir, 'model_metrics.json')
        with open(metrics_path, 'r') as f:
            self.metrics = json.load(f)
        
        # Verify model checksum
        with open(model_path, 'rb') as f:
            actual_hash = hashlib.sha256(f.read()).hexdigest()[:16]
        
        expected_hash = self.registry.get("model_hash", "")
        if actual_hash != expected_hash:
            logger.warning(
                f"Model checksum mismatch! Expected {expected_hash}, got {actual_hash}. "
                "The model file may have been modified since training."
            )
        else:
            logger.info(f"Model checksum verified: {actual_hash}")
        
        self._initialized = True
        logger.info(
            f"ModelService ready. Model: {self.registry['model_name']} "
            f"v{self.registry['model_version']}"
        )
    
    @property
    def is_ready(self) -> bool:
        """Check if all artifacts are loaded and ready for inference."""
        return self._initialized
    
    @property
    def model_version(self) -> str:
        return self.registry.get("model_version", "unknown") if self._initialized else "not_loaded"
    
    @property
    def model_hash(self) -> str:
        return self.registry.get("model_hash", "unknown") if self._initialized else "not_loaded"


# Global singleton instance
model_service = ModelService()
