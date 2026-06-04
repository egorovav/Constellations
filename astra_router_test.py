import astra_router as ar
import constellation_repository as repo

repository = repo.ConstellationRepository()
astra_router = ar.AstraRouter()

if __name__ == "__main__":
    # Alpha Centauri to Deneb
    # result = astra_router.get_route(32263, 101767, 50)
    result = astra_router.get_route(45, 456, 120)
    #result = repository.get_all_coordinates()
    print(f"{len(result)}")
    astra_router.print_route(result)
        


    