/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GisFeatureEnum } from './GisFeatureEnum';
/**
 * Serializa objetos Building al estándar GeoJSON.
 */
export type Building = {
    type?: GisFeatureEnum;
    readonly id?: number;
    geometry?: {
        type?: Building.type;
        coordinates?: Array<Array<Array<number>>>;
    };
    properties?: {
        /**
         * ID del edificio en planos externos
         */
        external_id?: string | null;
        name?: string;
        /**
         * Código identificador del edificio (ej: EPS-I)
         */
        code?: string;
        campus?: number;
    };
};
export namespace Building {
    export enum type {
        POLYGON = 'Polygon',
    }
}

