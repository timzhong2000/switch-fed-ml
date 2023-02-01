#include "server.h"
#include "tensor.h"
#include "client.h"
#include <memory>
#include <thread>
#include <vector>
#include <chrono>
#include <iostream>

using namespace switchfl;

int main()
{
    auto server = std::make_shared<Server>(NodeOptions{
        "127.0.0.1",
        50000,
        50001,
        1,
        false});
    auto client1 = std::make_shared<Client>(NodeOptions{
        "127.0.0.1",
        50002,
        50003,
        2,
        false});

    auto size = 256 * 1024 * 1024;
    auto tensor1 = std::make_shared<Tensor>(size, INT32_TYPE, 12345);
    auto tensor2 = std::make_shared<Tensor>(size, INT32_TYPE, 12345);
    memset(tensor2->seek(0), 2, size * sizeofDataType(INT32_TYPE));

    std::thread t0([&]
                   { server->receive_thread(); });
    std::thread t1([&]
                   { server->receive(*client1, 0, tensor1); });
    std::thread t2([&]
                   {sleep(1); 
                    client1->send(*server, 0, tensor2); });

    t2.join();
    t1.join();
    t0.join();

    return 0;
}
