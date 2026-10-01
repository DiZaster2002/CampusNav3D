/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { StatusEnum } from './StatusEnum';
/**
 * Serializador de lectura para el polling de estado y resultados.
 */
export type SpatialPlanStatus = {
    readonly id: number;
    status?: StatusEnum;
    /**
     * Archivo de imagen del plano (PNG/JPG/SVG)
     */
    image: string;
    /**
     * Hash SHA-256 del archivo
     */
    file_hash: string;
    /**
     * Esquema JSON normalizado de la propuesta
     */
    intermediate_proposal?: any;
    /**
     * Métricas de ejecución: {prompt, tokens_used, cost_usd, provider_name}
     */
    ai_metadata?: any;
    /**
     * Traza detallada del error si el estado es FAILED
     */
    error_log?: string | null;
    readonly created_at: string;
    readonly updated_at: string;
};

