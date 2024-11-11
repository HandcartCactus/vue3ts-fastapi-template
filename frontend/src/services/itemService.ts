import axiosInstance from '@/axios';
import axios from 'axios';
import qs from 'qs';


export class ItemError extends Error {
    constructor(message: string) {
        super(message);
        this.name = 'ItemError';
    }
}