-- Script SQL para criar tabela de ajustes de caminhões
-- Fox Control - Sistema de Agendamento de Cargas

-- Criar tabela para armazenar ajustes manuais de caminhões
CREATE TABLE IF NOT EXISTS fox_control_ajustes_caminhoes (
    id SERIAL PRIMARY KEY,
    carga_id INTEGER NOT NULL,
    caminhoes_manual INTEGER NOT NULL,
    caminhoes_calculado INTEGER NOT NULL,
    usuario VARCHAR(100),
    data_ajuste TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ativo BOOLEAN DEFAULT TRUE,
    observacoes TEXT,
    
    -- Campos adicionais para auditoria
    ip_usuario INET,
    user_agent TEXT,
    
    -- Índices para performance
    CONSTRAINT uk_carga_ativa UNIQUE (carga_id, ativo) DEFERRABLE INITIALLY DEFERRED
);

-- Criar índices para otimizar consultas
CREATE INDEX IF NOT EXISTS idx_ajustes_carga_id ON fox_control_ajustes_caminhoes(carga_id);
CREATE INDEX IF NOT EXISTS idx_ajustes_ativo ON fox_control_ajustes_caminhoes(ativo);
CREATE INDEX IF NOT EXISTS idx_ajustes_data ON fox_control_ajustes_caminhoes(data_ajuste);
CREATE INDEX IF NOT EXISTS idx_ajustes_usuario ON fox_control_ajustes_caminhoes(usuario);

-- Trigger para atualizar data_atualizacao automaticamente
CREATE OR REPLACE FUNCTION update_data_atualizacao()
RETURNS TRIGGER AS $$
BEGIN
    NEW.data_atualizacao = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_data_atualizacao
    BEFORE UPDATE ON fox_control_ajustes_caminhoes
    FOR EACH ROW
    EXECUTE FUNCTION update_data_atualizacao();

-- Função para desativar ajustes anteriores ao criar um novo
CREATE OR REPLACE FUNCTION desativar_ajustes_anteriores()
RETURNS TRIGGER AS $$
BEGIN
    -- Desativar todos os ajustes anteriores para a mesma carga
    UPDATE fox_control_ajustes_caminhoes 
    SET ativo = FALSE, data_atualizacao = CURRENT_TIMESTAMP
    WHERE carga_id = NEW.carga_id AND id != NEW.id AND ativo = TRUE;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_desativar_ajustes_anteriores
    AFTER INSERT ON fox_control_ajustes_caminhoes
    FOR EACH ROW
    EXECUTE FUNCTION desativar_ajustes_anteriores();

-- Comentários na tabela e colunas
COMMENT ON TABLE fox_control_ajustes_caminhoes IS 'Tabela para armazenar ajustes manuais do número de caminhões por carga';
COMMENT ON COLUMN fox_control_ajustes_caminhoes.carga_id IS 'ID da carga referenciando provisioningsv2_best_scenario_distance';
COMMENT ON COLUMN fox_control_ajustes_caminhoes.caminhoes_manual IS 'Número de caminhões definido manualmente';
COMMENT ON COLUMN fox_control_ajustes_caminhoes.caminhoes_calculado IS 'Número de caminhões calculado automaticamente';
COMMENT ON COLUMN fox_control_ajustes_caminhoes.usuario IS 'Usuário que fez o ajuste';
COMMENT ON COLUMN fox_control_ajustes_caminhoes.ativo IS 'Indica se o ajuste está ativo (apenas um por carga)';
COMMENT ON COLUMN fox_control_ajustes_caminhoes.observacoes IS 'Observações sobre o ajuste';

-- Inserir alguns dados de exemplo (opcional)
-- INSERT INTO fox_control_ajustes_caminhoes (carga_id, caminhoes_manual, caminhoes_calculado, usuario, observacoes)
-- VALUES 
--     (302, 3, 2, 'admin', 'Ajuste para otimizar rota'),
--     (303, 1, 1, 'admin', 'Mantido cálculo automático');

-- Consultas úteis para verificação:

-- 1. Ver todos os ajustes ativos
-- SELECT * FROM fox_control_ajustes_caminhoes WHERE ativo = TRUE ORDER BY data_ajuste DESC;

-- 2. Ver histórico de ajustes por carga
-- SELECT * FROM fox_control_ajustes_caminhoes WHERE carga_id = 302 ORDER BY data_ajuste DESC;

-- 3. Estatísticas de ajustes
-- SELECT 
--     COUNT(*) as total_ajustes,
--     COUNT(CASE WHEN ativo THEN 1 END) as ajustes_ativos,
--     COUNT(DISTINCT carga_id) as cargas_com_ajuste,
--     COUNT(DISTINCT usuario) as usuarios_distintos
-- FROM fox_control_ajustes_caminhoes;

-- 4. Ajustes por usuário
-- SELECT usuario, COUNT(*) as total_ajustes, COUNT(CASE WHEN ativo THEN 1 END) as ativos
-- FROM fox_control_ajustes_caminhoes 
-- GROUP BY usuario 
-- ORDER BY total_ajustes DESC;

