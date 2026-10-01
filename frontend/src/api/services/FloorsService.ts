/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Floor } from '../models/Floor';
import type { FloorList } from '../models/FloorList';
import type { PatchedFloor } from '../models/PatchedFloor';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class FloorsService {
    /**
     * @returns FloorList
     * @throws ApiError
     */
    public static floorsList(): CancelablePromise<FloorList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/floors/',
        });
    }
    /**
     * @param requestBody
     * @returns Floor
     * @throws ApiError
     */
    public static floorsCreate(
        requestBody?: Floor,
    ): CancelablePromise<Floor> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/floors/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @param id A unique integer value identifying this floor.
     * @returns Floor
     * @throws ApiError
     */
    public static floorsRetrieve(
        id: number,
    ): CancelablePromise<Floor> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/floors/{id}/',
            path: {
                'id': id,
            },
        });
    }
    /**
     * @param id A unique integer value identifying this floor.
     * @param requestBody
     * @returns Floor
     * @throws ApiError
     */
    public static floorsUpdate(
        id: number,
        requestBody?: Floor,
    ): CancelablePromise<Floor> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/floors/{id}/',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @param id A unique integer value identifying this floor.
     * @param requestBody
     * @returns Floor
     * @throws ApiError
     */
    public static floorsPartialUpdate(
        id: number,
        requestBody?: PatchedFloor,
    ): CancelablePromise<Floor> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/floors/{id}/',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @param id A unique integer value identifying this floor.
     * @returns void
     * @throws ApiError
     */
    public static floorsDestroy(
        id: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/floors/{id}/',
            path: {
                'id': id,
            },
        });
    }
}
