/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * * `UPLOADED` - Cargado / Pendiente
 * * `PREPROCESSING` - Preprocesando Imagen
 * * `EXTRACTING` - Extrayendo con IA
 * * `REQUIRES_REVIEW` - Requiere Revisión Manual
 * * `PROCESSED` - Procesado Completamente
 * * `APPROVED` - Aprobado y Persistido
 * * `REJECTED` - Rechazado por el Revisor
 * * `FAILED` - Error en el Pipeline
 */
export enum StatusEnum {
    UPLOADED = 'UPLOADED',
    PREPROCESSING = 'PREPROCESSING',
    EXTRACTING = 'EXTRACTING',
    REQUIRES_REVIEW = 'REQUIRES_REVIEW',
    PROCESSED = 'PROCESSED',
    APPROVED = 'APPROVED',
    REJECTED = 'REJECTED',
    FAILED = 'FAILED',
}
