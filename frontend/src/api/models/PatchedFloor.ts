/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GisFeatureEnum } from './GisFeatureEnum';
/**
 * Serializa objetos Floor al estándar GeoJSON.
 */
export type PatchedFloor = {
    type?: GisFeatureEnum;
    readonly id?: number;
    geometry?: {
        type?: PatchedFloor.type;
        coordinates?: Array<Array<Array<number>>>;
    };
    properties?: {
        /**
         * ID de la planta en planos externos
         */
        external_id?: string | null;
        /**
         * Número de planta (0=Baja, 1=Primera, -1=Sótano)
         */
        level?: number;
        /**
         * Nombre de la planta (ej: Planta Primera)
         */
        name?: string;
        /**
         * Altitud relativa en metros desde el suelo
         */
        altitude?: number;
        building?: number;
    };
};
export namespace PatchedFloor {
    export enum type {
        POLYGON = 'Polygon',
    }
}

