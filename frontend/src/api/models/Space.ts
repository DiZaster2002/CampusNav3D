/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GisFeatureEnum } from './GisFeatureEnum';
/**
 * Serializa las celdas IndoorGML al estándar GeoJSON.
 */
export type Space = {
    type?: GisFeatureEnum;
    readonly id?: number;
    geometry?: {
        type?: Space.type;
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
        space_type?: Space.space_type;
        floor?: number;
    };
};
export namespace Space {
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

