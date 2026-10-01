/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GisFeatureEnum } from './GisFeatureEnum';
/**
 * Serializa las conexiones del grafo al estándar GeoJSON.
 */
export type NavigationEdge = {
    type?: GisFeatureEnum;
    readonly id?: number;
    geometry?: {
        type?: NavigationEdge.type;
        coordinates?: Array<Array<number>>;
    };
    properties?: {
        /**
         * Nombre opcional de la conexión (ej: Pasillo-Aula101)
         */
        name?: string;
        /**
         * Espacio de origen (Nodo A)
         */
        source_space?: number;
        /**
         * Espacio de destino (Nodo B)
         */
        target_space?: number;
        /**
         * Indica si este tramo es apto para personas con movilidad reducida (sin escaleras)
         */
        is_accessible?: boolean;
    };
};
export namespace NavigationEdge {
    export enum type {
        LINE_STRING = 'LineString',
    }
}

