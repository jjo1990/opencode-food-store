/**
 * Example test demonstrating Jest + React Testing Library setup
 */

describe('Example Test Suite', () => {
  it('should pass a simple test', () => {
    expect(true).toBe(true);
  });

  it('should do basic arithmetic', () => {
    const result = 2 + 2;
    expect(result).toBe(4);
  });

  it('should compare objects', () => {
    const person = {
      name: 'Alice',
      age: 30,
    };
    expect(person).toEqual({ name: 'Alice', age: 30 });
  });
});
