/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Building } from '../models/Building';
import type { BuildingList } from '../models/BuildingList';
import type { PatchedBuilding } from '../models/PatchedBuilding';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class BuildingsService {
    /**
     * @returns BuildingList
     * @throws ApiError
     */
    public static buildingsList(): CancelablePromise<BuildingList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/buildings/',
        });
    }
    /**
     * @param requestBody
     * @returns Building
     * @throws ApiError
     */
    public static buildingsCreate(
        requestBody?: Building,
    ): CancelablePromise<Building> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/buildings/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @param id A unique integer value identifying this building.
     * @returns Building
     * @throws ApiError
     */
    public static buildingsRetrieve(
        id: number,
    ): CancelablePromise<Building> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/buildings/{id}/',
            path: {
                'id': id,
            },
        });
    }
    /**
     * @param id A unique integer value identifying this building.
     * @param requestBody
     * @returns Building
     * @throws ApiError
     */
    public static buildingsUpdate(
        id: number,
        requestBody?: Building,
    ): CancelablePromise<Building> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/buildings/{id}/',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @param id A unique integer value identifying this building.
     * @param requestBody
     * @returns Building
     * @throws ApiError
     */
    public static buildingsPartialUpdate(
        id: number,
        requestBody?: PatchedBuilding,
    ): CancelablePromise<Building> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/buildings/{id}/',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @param id A unique integer value identifying this building.
     * @returns void
     * @throws ApiError
     */
    public static buildingsDestroy(
        id: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/buildings/{id}/',
            path: {
                'id': id,
            },
        });
    }
}
