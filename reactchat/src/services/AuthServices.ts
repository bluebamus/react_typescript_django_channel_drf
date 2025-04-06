import axios from "axios";
import { AuthServiceProps } from "../@types/auth-service";
import { useState } from "react";
import { BASE_URL } from "../config";
import { useNavigate } from "react-router-dom";


export function useAuthService(): AuthServiceProps {

    const navigate = useNavigate()

    const getInitialLoggedInValue = () => {
        const loggedIn = localStorage.getItem("isLoggedIn");
        return loggedIn !== null && loggedIn === "true";
      };

    const [isLoggedIn, setIsLoggedIn] = useState<boolean>((getInitialLoggedInValue))
    
    const getUserDetails = async () =>{
        try {
            const userId = localStorage.getItem("user_id")
            const response = await axios.get(
                `http://127.0.0.1:8000/api/account/?user_id=${userId}`,
                {
                    withCredentials: true
                }
            );
            const userDetails = response.data
            localStorage.setItem("username", userDetails.username);
            setIsLoggedIn(true);
            localStorage.setItem("isLoggedIn", "true")
        } catch (err: any) {
            setIsLoggedIn(false)
            localStorage.setItem("isLoggedIn", "false")
            return err;
        }
    }

    // utils.ts나 같은 파일 안
    const getCookie = (name: string): string | null => {
        const cookieValue = document.cookie
            .split("; ")
            .find((row) => row.startsWith(`${name}=`));
        return cookieValue ? decodeURIComponent(cookieValue.split("=")[1]) : null;
    };

    const login = async (username: string, password: string) =>{
        try {
            const response = await axios.post(
                "http://127.0.0.1:8000/api/token/", {
                    username,
                    password,
            }, { withCredentials: true }
            );

            console.log("로그인 응답 데이터:", response.data);  // 👈 전체 응답 확인
            console.log("user_id:", response.data.user_id);

            // 👇 쿠키에 access_token, refresh_token 확인
            console.log("access_token (쿠키):", getCookie("access_token"));
            console.log("refresh_token (쿠키):", getCookie("refresh_token"));

            const user_id = response.data.user_id
            localStorage.setItem("isLoggedIn", "true")
            localStorage.setItem("user_id", user_id)
            setIsLoggedIn(true)
            getUserDetails()

        } catch (err: any) {
            return err.response.status;
        }
    }

    const refreshAccessToken = async () => {
        try {
            await axios.post(
                `${BASE_URL}/token/refresh/`, {} , {withCredentials:true}
            )
        } catch (refreshError) {
            return Promise.reject(refreshError)
        }
    }

    const register = async (username: string, password: string) =>{
        try {
            const response = await axios.post(
                "http://127.0.0.1:8000/api/register/", {
                    username,
                    password,
            }, { withCredentials: true }
            );
            return response.status
        } catch (err: any) {
            return err.response.status;
        }
    }


    const logout = async () => {
        localStorage.setItem("isLoggedIn", "false")
        localStorage.removeItem("user_id")
        localStorage.removeItem("username");
        setIsLoggedIn(false);
        navigate("/login")

        try {
            await axios.post(
                `${BASE_URL}/logout/`, {} , {withCredentials:true}
            )
        } catch (refreshError) {
            return Promise.reject(refreshError)
        }

    }

    return {login, isLoggedIn, logout, refreshAccessToken, register}
   
}