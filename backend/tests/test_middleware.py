class TestLoggingMiddleware:
    def test_request_id_in_response_header(self, client):
        """X-Request-ID header MUST be present in all responses."""
        response = client.get("/api/v1/productos")
        assert "X-Request-ID" in response.headers
        assert len(response.headers["X-Request-ID"]) > 0

    def test_health_endpoint_not_crash(self, client):
        """Health check endpoints should not crash with middleware."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_root_endpoint_not_crash(self, client):
        """Root endpoint should not crash with middleware."""
        response = client.get("/")
        assert response.status_code == 200

    def test_404_response_has_request_id(self, client):
        """404 responses should still have X-Request-ID header."""
        response = client.get("/api/v1/productos/nonexistent")
        assert "X-Request-ID" in response.headers
        assert len(response.headers["X-Request-ID"]) > 0
