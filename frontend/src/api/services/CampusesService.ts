/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Campus } from '../models/Campus';
import type { CampusList } from '../models/CampusList';
import type { PatchedCampus } from '../models/PatchedCampus';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class CampusesService {
    /**
     * @returns CampusList
     * @throws ApiError
     */
    public static campusesList(): CancelablePromise<CampusList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/campuses/',
        });
    }
    /**
     * @param requestBody
     * @returns Campus
     * @throws ApiError
     */
    public static campusesCreate(
        requestBody?: Campus,
    ): CancelablePromise<Campus> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/campuses/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @param id A unique integer value identifying this campus.
     * @returns Campus
     * @throws ApiError
     */
    public static campusesRetrieve(
        id: number,
    ): CancelablePromise<Campus> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/campuses/{id}/',
            path: {
                'id': id,
            },
        });
    }
    /**
     * @param id A unique integer value identifying this campus.
     * @param requestBody
     * @returns Campus
     * @throws ApiError
     */
    public static campusesUpdate(
        id: number,
        requestBody?: Campus,
    ): CancelablePromise<Campus> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/campuses/{id}/',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @param id A unique integer value identifying this campus.
     * @param requestBody
     * @returns Campus
     * @throws ApiError
     */
    public static campusesPartialUpdate(
        id: number,
        requestBody?: PatchedCampus,
    ): CancelablePromise<Campus> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/campuses/{id}/',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @param id A unique integer value identifying this campus.
     * @returns void
     * @throws ApiError
     */
    public static campusesDestroy(
        id: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/campuses/{id}/',
            path: {
                'id': id,
            },
        });
    }
}
