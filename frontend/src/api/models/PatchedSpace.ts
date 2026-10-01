/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GisFeatureEnum } from './GisFeatureEnum';
/**
 * Serializa las celdas IndoorGML al estándar GeoJSON.
 */
export type PatchedSpace = {
    type?: GisFeatureEnum;
    readonly id?: number;
    geometry?: {
        type?: PatchedSpace.type;
        coordinates?: Array<Array<Array<number>>>;
    };
    properties?: {
        /**
         * ID del espacio en planos externos
         */
        external_id?: string | null;
        /**
         * Ej: Aula 1.1, Despacho 202
         */
        name?: string;
        /**
         * * `ROOM` - Aula / Despacho
         * * `CORRIDOR` - Pasillo / Zona de Circulación
         * * `STAIRS` - Escaleras
         * * `ELEVATOR` - Ascensor
         * * `RESTROOM` - Servicios / Aseos
         * * `RESTRICTED` - Zona Restringida / Técnica
         */
        space_type?: PatchedSpace.space_type;
        floor?: number;
    };
};
export namespace PatchedSpace {
    export enum type {
        POLYGON = 'Polygon',
    }
    /**
     * * `ROOM` - Aula / Despacho
     * * `CORRIDOR` - Pasillo / Zona de Circulación
     * * `STAIRS` - Escaleras
     * * `ELEVATOR` - Ascensor
     * * `RESTROOM` - Servicios / Aseos
     * * `RESTRICTED` - Zona Restringida / Técnica
     */
    export enum space_type {
        ROOM = 'ROOM',
        CORRIDOR = 'CORRIDOR',
        STAIRS = 'STAIRS',
        ELEVATOR = 'ELEVATOR',
        RESTROOM = 'RESTROOM',
        RESTRICTED = 'RESTRICTED',
    }
}

