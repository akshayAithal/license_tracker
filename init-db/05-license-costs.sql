-- ============================================================================
-- License Costs Table + Seed Data
-- Real-world approximate license costs for simulation/CAE vendors
-- ============================================================================

CREATE TABLE IF NOT EXISTS license_costs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vendor VARCHAR(64) NOT NULL,
    feature VARCHAR(128) NOT NULL,
    cost_per_license FLOAT NOT NULL DEFAULT 0.0,
    currency VARCHAR(8) DEFAULT 'USD',
    billing_period VARCHAR(32) DEFAULT 'annual',
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_vendor_feature (vendor, feature)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- AI/Model settings in app_settings
INSERT INTO app_settings (setting_key, setting_value, setting_type, description) VALUES
    ('ai_provider', 'openai', 'string', 'AI provider: openai or local'),
    ('openai_api_key', '', 'string', 'OpenAI API key for document analysis'),
    ('openai_model', 'gpt-4o-mini', 'string', 'OpenAI model name'),
    ('local_model_url', '', 'string', 'Local LLM API URL (OpenAI-compatible)'),
    ('local_model_name', 'default', 'string', 'Local LLM model name'),
    ('local_model_api_key', '', 'string', 'Local LLM API key (if required)')
ON DUPLICATE KEY UPDATE setting_key=setting_key;

-- ============================================================================
-- Altair License Costs (approximate annual per-seat, USD)
-- Source: industry estimates, Altair Units pricing ~$100-$130/unit/year
-- HyperWorks uses Altair Units (AU) model since 2019
-- ============================================================================
INSERT INTO license_costs (vendor, feature, cost_per_license, currency, billing_period, notes) VALUES
    ('Altair', 'HyperWorks', 12000.00, 'USD', 'annual', 'HyperWorks Enterprise bundle - approx 100 Altair Units at ~$120/unit'),
    ('Altair', 'HyperMesh', 8500.00, 'USD', 'annual', 'Pre/post-processor - typically 70 AU'),
    ('Altair', 'Radioss', 15000.00, 'USD', 'annual', 'Explicit FE solver - approx 125 AU per run'),
    ('Altair', 'OptiStruct', 14000.00, 'USD', 'annual', 'Optimization solver - approx 115 AU'),
    ('Altair', 'MotionSolve', 10000.00, 'USD', 'annual', 'Multi-body dynamics - approx 80 AU'),
    ('Altair', 'AcuSolve', 12000.00, 'USD', 'annual', 'CFD solver - approx 100 AU'),
    ('Altair', 'SimLab', 7500.00, 'USD', 'annual', 'Process-oriented meshing - approx 60 AU'),
    ('Altair', 'Inspire', 6000.00, 'USD', 'annual', 'Generative design/topology optimization - approx 50 AU')
ON DUPLICATE KEY UPDATE cost_per_license=VALUES(cost_per_license), notes=VALUES(notes);

-- ============================================================================
-- MSC Software License Costs (approximate annual per-seat, USD)
-- Source: industry estimates, MSC traditional per-feature licensing
-- ============================================================================
INSERT INTO license_costs (vendor, feature, cost_per_license, currency, billing_period, notes) VALUES
    ('MSC', 'Nastran', 18000.00, 'USD', 'annual', 'MSC Nastran - industry standard FEA solver'),
    ('MSC', 'Patran', 8000.00, 'USD', 'annual', 'Pre/post-processing for Nastran'),
    ('MSC', 'Marc', 22000.00, 'USD', 'annual', 'Advanced nonlinear FEA solver'),
    ('MSC', 'Adams', 20000.00, 'USD', 'annual', 'Multi-body dynamics simulation'),
    ('MSC', 'Digimat', 15000.00, 'USD', 'annual', 'Multi-scale material modeling'),
    ('MSC', 'Simufact', 16000.00, 'USD', 'annual', 'Manufacturing process simulation'),
    ('MSC', 'Apex', 10000.00, 'USD', 'annual', 'CAE environment for Nastran')
ON DUPLICATE KEY UPDATE cost_per_license=VALUES(cost_per_license), notes=VALUES(notes);

-- ============================================================================
-- Particleworks License Costs (approximate annual per-seat, USD)
-- Source: Prometech Software pricing estimates
-- MPS (Moving Particle Simulation) method for fluid dynamics
-- ============================================================================
INSERT INTO license_costs (vendor, feature, cost_per_license, currency, billing_period, notes) VALUES
    ('Particleworks', 'Particleworks', 25000.00, 'USD', 'annual', 'MPS-based particle simulation for free-surface flows'),
    ('Particleworks', 'Particleworks/GPU', 35000.00, 'USD', 'annual', 'GPU-accelerated particle simulation'),
    ('Particleworks', 'Granuleworks', 20000.00, 'USD', 'annual', 'DEM-based granular flow simulation')
ON DUPLICATE KEY UPDATE cost_per_license=VALUES(cost_per_license), notes=VALUES(notes);

-- ============================================================================
-- RLM / Masta / Ricardo License Costs (approximate, USD)
-- ============================================================================
INSERT INTO license_costs (vendor, feature, cost_per_license, currency, billing_period, notes) VALUES
    ('RLM', 'Masta', 18000.00, 'USD', 'annual', 'SMT MASTA - drivetrain/gear design and analysis'),
    ('RLM', 'Masta_Advanced', 25000.00, 'USD', 'annual', 'MASTA Advanced - NVH, durability, system-level'),
    ('Ricardo', 'WAVE', 15000.00, 'USD', 'annual', 'Ricardo WAVE - 1D engine/gas dynamics simulation'),
    ('Ricardo', 'VECTIS', 20000.00, 'USD', 'annual', 'Ricardo VECTIS - 3D CFD for IC engines'),
    ('Ricardo', 'SABR', 12000.00, 'USD', 'annual', 'Ricardo SABR - bearing analysis')
ON DUPLICATE KEY UPDATE cost_per_license=VALUES(cost_per_license), notes=VALUES(notes);
