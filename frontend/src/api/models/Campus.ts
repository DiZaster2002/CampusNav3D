/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GisFeatureEnum } from './GisFeatureEnum';
/**
 * Serializa objetos Campus al estándar GeoJSON.
 */
export type Campus = {
    type?: GisFeatureEnum;
    readonly id?: number;
    geometry?: {
        type?: Campus.type;
        coordinates?: Array<Array<Array<number>>>;
    };
    properties?: {
        /**
         * ID del campus en planos externos
         */
        external_id?: string | null;
        name?: string;
        slug?: string;
        readonly created_at?: string;
    };
};
export namespace Campus {
    export enum type {
        POLYGON = 'Polygon',
    }
}

