import axiosInstance from '@/axios';
import axios from 'axios';
import qs from 'qs';

export class AuthError extends Error {
    constructor(message: string) {
        super(message);
        this.name = 'AuthError';
    }
}

export class Token {
  public token: string;
  public tokenType: string;

  constructor(token: string, tokenType: string){
    this.token = token;
    this.tokenType = tokenType;
   }
}

export class OtpSetup {
  public provisioningUri: string;
  public qrCodeBase64: string;

  constructor(provisioningUri: string, qrCodeBase64: string) {
    this.provisioningUri = provisioningUri;
    this.qrCodeBase64 = qrCodeBase64;
  }
}

export class OtpChallenge {
}

export async function verify2fa(username:string, otp:string): Promise<Token> {
    try {
        const response = await axiosInstance.post(
            '/auth/verify-2fa?'+ 
            qs.stringify(
              {
                username: username,
                otp: otp,
              }
            ),
            null, 
            { 
              headers: { 
                'Content-Type': 'application/x-www-form-urlencoded' 
              } 
            }
        );
        return new Token(response.data.access_token, response.data.token_type);
    } catch (err) {
        if (axios.isAxiosError(err)) {
            const status = err.response?.status
            if (status === 401) {
              throw new AuthError('Invalid 2FA code.')
            } else if (status === 404) {
              throw new AuthError('2FA not enabled for this user.')
            } else {
              throw new AuthError('An unexpected error occurred.')
            }
        }
    }

    throw new AuthError('An unexpected error occurred.');
}

export async function enable2fa(accessToken:string): Promise<OtpSetup> {
  try {
    const response = await axiosInstance.post('/auth/enable-2fa', null, {headers: { Authorization: `Bearer ${accessToken}` }, })
    return new OtpSetup(
      response.data.provisioning_uri, 
      response.data.qr_code_base64
    );
  } catch (err) {
    if (axios.isAxiosError(err)) {
      // split in case additional handling or different message is required
      throw new AuthError('An unexpected error occurred while enabling 2FA.');
    } else {
      throw new AuthError('An unexpected error occurred while enabling 2FA.');
    }
  }
}

export async function registerUser(username:string, password:string): Promise<Token> {
  try {
    const response = await axiosInstance.post('/auth/register', {
      username: username,
      password: password,
    })
    return new Token(response.data.access_token, response.data.token_type);
  } catch (err) {
    if (axios.isAxiosError(err)) {
      const status = err.response?.status
      if (status === 409) {
        throw new AuthError('Username already exists.')
      }
    }
  }
  throw new AuthError('An unexpected error occurred.')
}

export async function loginUser(username:string, password:string): Promise<Token|OtpChallenge> {
  try {
    const response = await axiosInstance.post('/auth/token', qs.stringify({
      username: username,
      password: password,
      grant_type: 'password',
    }), { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } })
    if (!response.data.requires_2fa) {
      return new Token(response.data.access_token, response.data.token_type);
    } else {
      return new OtpChallenge();
    }
  } catch (err) {
    if (axios.isAxiosError(err)) {
      const status = err.response?.status
      if (status === 401) {
        throw new AuthError('Incorrect username or password.')
      }
    }
  }
  throw new AuthError('An unexpected error occurred.')
}