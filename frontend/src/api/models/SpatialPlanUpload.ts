/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Serializador para la carga inicial de un plano espacial.
 */
export type SpatialPlanUpload = {
    readonly id: number;
    /**
     * Archivo de imagen del plano (PNG/JPG/SVG)
     */
    image: string;
    /**
     * Nombre del modelo objetivo (ej: 'campus', 'building', 'floor')
     */
    model_type: string;
    /**
     * ID del objeto objetivo
     */
    target_id: number;
    ai_provider?: string;
    readonly created_at: string;
};

