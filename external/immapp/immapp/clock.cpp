#include "immapp/immapp.h"
#include <chrono>


namespace ImmApp
{

    class ClockSeconds_
    {
        // Typical C++ shamanic incantations to get a time in seconds
    private:
        using Clock = std::chrono::high_resolution_clock;
        using second = std::chrono::duration<double, std::ratio<1>>;
        std::chrono::time_point<Clock> mStart;

    public:
        ClockSeconds_() : mStart(Clock::now()) {}

        double elapsed() const
        {
            return std::chrono::duration_cast<second>
                (Clock::now() - mStart).count();
        }
    };

    double ClockSeconds()
    {
        static ClockSeconds_ watch;
        return watch.elapsed();
    }

} // namespace ImmApp
