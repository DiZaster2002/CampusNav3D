/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { StatusEnum } from './StatusEnum';
/**
 * Serializador resumido para listar todos los planos registrados.
 */
export type SpatialPlanList = {
    readonly id: number;
    status?: StatusEnum;
    /**
     * Hash SHA-256 del archivo
     */
    file_hash: string;
    /**
     * Traza detallada del error si el estado es FAILED
     */
    error_log?: string | null;
    readonly created_at: string;
    readonly updated_at: string;
};

