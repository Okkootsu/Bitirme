import { Button } from "@/components/Button";
import { useNavigate } from "react-router-dom";

export const AboutPage = () => {
  const navigate = useNavigate();

  return (
    <div className="flex-1 flex flex-col items-center justify-center bg-amber-50 ">
      <h1>Hakkımızda Sayfası</h1>
      <p>Test</p>

      <div style={{ marginTop: "20px" }}>
        <Button onClick={() => navigate("/")}>Ana Sayfaya Dön</Button>
      </div>
    </div>
  );
};
